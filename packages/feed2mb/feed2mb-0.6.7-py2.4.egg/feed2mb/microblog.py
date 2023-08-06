# feed2mb
# Copyright (C) 2009 Walter Cruz <walter@waltercruz.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from twitter import Api
import readrss
from shortener import services
from httplib import BadStatusLine
from urllib2 import HTTPError
import time
import re

class Microblog(object):
    def strip_tags(self,value):
        "Return the given HTML with all tags stripped."
        txt = re.sub(r'<[^>]*?>', '', value.replace('\t','').replace('\n','')) 
        return txt.replace('(Comments)','')

    def update(self):
        lastread = self.rss.getlastRead()
        if not lastread:
            self.postIt(reversed(self.rss.feed['items'][:self.items]))
        else:
            try:
                lista = [item for item in self.rss.feed['items'] if item['published_parsed'] > lastread]
            except:
                lista = [item for item in self.rss.feed['items'] if item['updated_parsed'] > lastread]
            self.postIt(reversed(lista[:self.items]))

    def postIt(self, items):
        oldItems=pItems=0
        for it in list(items):
            if self.mode == 'title':
                txt=it["title"][0:114] +" "+self.shortener.short(it["link"])
            elif self.mode == 'text':
                try:
                    txt = self.strip_tags(it.content[0].value)[0:140]
                except:
                    txt = self.strip_tags(it.summary)[0:140]
            else:
                txt = it['title'][0:144] + " " + tiny(it['link'])
            try:
                status = self.api.PostUpdate(txt)
                self.rss.updateLastRead(it)
                print "status: ", status.text
                time.sleep(5)

            except (BadStatusLine, HTTPError):
                #lets try in the next time
                return

class IdenticaAPI(Api):

    _API_REALM = 'Laconica API'

    def PostUpdate(self, text):
        import simplejson
        from twitter import Status
        from twitter import TwitterError
        '''Post a twitter status message from the authenticated user.
        
        The twitter.Api instance must be authenticated.

        Args:
        text: The message text to be posted.  Must be less than 140 characters.

        Returns:
        A twitter.Status instance representing the message posted
        '''
        if not self._username:
            raise TwitterError("The twitter.Api instance must be authenticated.")
        if len(text) > 140:
            raise TwitterError("Text must be less than or equal to 140 characters.")
        url = 'https://identi.ca/api/statuses/update.json'
        data = {'status': text}
        json = self._FetchUrl(url, post_data=data)
        data = simplejson.loads(json)
        return Status.NewFromJsonDict(data)

    def _GetOpener(self, url, username=None, password=None):
        import urlparse, urllib2
        if username and password:
            self._AddAuthorizationHeader(username, password)
            handler = self._urllib.HTTPBasicAuthHandler()
            (scheme, netloc, path, params, query, fragment) = urlparse.urlparse(url)
            handler.add_password(IdenticaAPI._API_REALM, netloc, username, password)
            opener = self._urllib.build_opener(handler)#,urllib2.HTTPHandler(debuglevel=1))
        else:
            opener = self._urllib.build_opener()
            opener.addheaders = self._request_headers.items()
        return opener


class Twitter(Microblog):
    def __init__(self,  url, username, passwd, mode='title', items = 5, shortener='tinyurl'):
        self.mode = mode
        self.url = url
        self.items = items
        self.username = username
        self.passwd = passwd
        self.api = Api(username=self.username, password=self.passwd)
        self.rss = readrss.parse(url)
        self.shortener = services[shortener]()

class Identica(Microblog):
    def __init__(self,  url, username, passwd, mode='title', items = 5, shortener='tinyurl'):
        self.mode = mode
        self.url = url
        self.items = items
        self.username = username
        self.passwd = passwd
        self.api = IdenticaAPI(username=self.username, password=self.passwd)
        self.rss = readrss.parse(url)
        self.shortener = services[shortener]()

service = {
    'twitter' : Twitter,
    'identica' : Identica,
}
