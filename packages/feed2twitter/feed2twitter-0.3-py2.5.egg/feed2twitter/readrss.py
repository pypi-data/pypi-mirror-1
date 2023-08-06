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

import feedparser, pickle, time
import os.path
from os import mkdir
import md5

class parse(object):

    def __init__(self,feed_url):
        self.feed_url = feed_url
        self.feed = feedparser.parse(feed_url)

    def getStampFileName(self):
        self.md5name = md5.md5(self.feed_url).hexdigest()
        self.directory = os.path.expanduser("~/.feed2twitter/")
        self.filename = self.directory + self.md5name

    def updateLastRead(self,item=None):
        self.getStampFileName()
        if not os.path.exists(self.directory):
            mkdir(self.directory)
        output = open(self.filename, 'wb')
        if not item:
            pickle.dump(self.feed['items'][0]['updated_parsed'], output)
        else:
            pickle.dump(item['updated_parsed'], output)
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



