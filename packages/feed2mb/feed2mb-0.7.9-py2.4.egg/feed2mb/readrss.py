# -*- coding: utf-8 -*-
# feed2mb
# Copyright (C) 2008 EBC - Empresa Brasil de Comunicação
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

import feedparser, pickle, time
import os.path
from os import mkdir
import md5

class parse(object):

    def __init__(self,feed_url,service):
        self.feed_url = feed_url
        self.service = service
        self.feed = feedparser.parse(feed_url)

    def getStampFileName(self):
        self.md5name = md5.md5(self.feed_url + self.service).hexdigest()
        self.directory = os.path.expanduser("~/.feed2mb/")
        self.filename = self.directory + self.md5name

    def updateLastRead(self,item=None):
        self.getStampFileName()
        if not os.path.exists(self.directory):
            mkdir(self.directory)
        output = open(self.filename, 'wb')
        key = 'updated_parsed'
        if not item:
            if 'published_parsed' in self.feed['items'][0]:
                key = 'published_parsed'
            pickle.dump(self.feed['items'][0][key], output)
        else:
            if 'published_parsed' in item:
                key = 'published_parsed'
            else:
                key = 'updated_parsed'
            pickle.dump(item[key], output)
        output.close()

    def getlastRead(self):
        self.getStampFileName()
        try:
            pick = open(self.filename, 'rb')
        except IOError:
            return False
        try:
            last_read = pickle.load(pick)
        except EOFError:
            return False
        return last_read



