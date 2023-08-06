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

from optparse import OptionParser
import sys

class Options(object):
    def __init__(self):
        self.parser = OptionParser()
        self.parser.add_option("-c", "--config", dest="config_filename",
                  help="name of the file to read the settings", metavar="FILE")
        self.parser.add_option("-p", "--print_sample_config",
                  action="store_true", dest="sample_config", default=False,
                  help="print a sample config file and exit")
    def parse(self):
        (options, args) = self.parser.parse_args()
        if not options.config_filename and not options.sample_config:
            self.parser.print_help()
            sys.exit()
        return options
