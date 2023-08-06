# feed2twitter
# Copyright (C) 2008 Walter Cruz <walter@waltercruz.com>
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

import feedparser, pickle, os, sys, urllib, twitter
from ConfigParser import ConfigParser, NoOptionError
from options import Options
import re, time
from pprint import pprint
from parsetime import parsetime
import microblog

def update(**kwargs):
    if not kwargs:
        opt = Options()
        options = opt.parse()
        conf = ConfigParser()
        if options.sample_config:
            from pkg_resources import resource_string
            foo_config = resource_string(__name__, '../docs/default.cfg.sample')
            print(foo_config)
            sys.exit(1)
        try:
            fd =  open(options.config_filename, 'r')
        except IOError:
            print >>sys.stderr, "File %s not found" % configfile
            sys.exit(2)
        conf.readfp(fd)

        url = conf.get("global", "url").strip()
        service = conf.get("global", "service").strip()
        username = conf.get("global", "username").strip()
        password = conf.get("global", "password").strip()
        mode = conf.get("global","mode").strip()
        try:
            items = int(conf.get("global","items").strip())
        except NoOptionError:
            items = 5

        try:
            interval = parsetime(conf.get("global","interval").strip())
        except:
            print('Error in the interval setting')
            sys.exit(1)

        try:
            shortener = conf.get('global','shortener').strip()
        except NoOptionError:
            shortener = 'tinyurl'
    else:
        url = kwargs['url']
        username = kwargs['username']
        password = kwargs['password']
        mode = kwargs['mode']
        items = 5
        shortener = kwargs['shortener']
        interval = parsetime('00:05')
        service = kwargs['service']

    while True:
        the_service = microblog.service[service](url, username, password, mode, items, shortener)
        the_service.update()
        time.sleep(interval)

__version__ = '0.6.6'

