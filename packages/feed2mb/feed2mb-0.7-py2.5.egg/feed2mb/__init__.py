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

from config import MicroblogConfig
import microblog
import logging
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

def update(**kwargs):
    if not kwargs:
        opt = Options()
        options = opt.parse()
        conf = MicroblogConfig(options.config_filename)
        if options.sample_config:
            from pkg_resources import resource_string
            foo_config = resource_string(__name__, '../docs/default.cfg.sample')
            print(foo_config)
            sys.exit(1)
        if options.log_filename:
            fh = logging.FileHandler(options.log_filename)
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            fh.setFormatter(formatter)
            log.addHandler(fh)
#            microblog.log.addHandler(fh)
        else:
            logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            )
        configs = conf.configs()
    else:
        configs=[]
        kwargs['items'] = 5
        configs.append(kwargs)
        url = kwargs['url']
        shortener = kwargs['shortener']
        kwargs['interval'] = parsetime('00:05')

    log.debug('Starting feed2mb')
    while True:
        interval = configs[0]['interval']
        for cf in configs:
            the_service = microblog.service(**cf).get()
            the_service.update()
            log.debug('next ' + cf['service'] + ' update in: ' + str(interval) + ' seconds')
        time.sleep(interval)

__version__ = '0.7'

