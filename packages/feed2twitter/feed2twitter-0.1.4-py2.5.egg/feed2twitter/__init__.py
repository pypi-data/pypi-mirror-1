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

import feedparser, pickle, os, sys, twitter, urllib
from ConfigParser import ConfigParser, NoOptionError
import readrss
import time
from pprint import pprint
from tinyurl import tiny
from httplib import BadStatusLine
from urllib2 import HTTPError

class Feed2Twitter(object):
    def __init__(self,  url, username, passwd):
      self.url=url
      self.username=username
      self.passwd=passwd
      self.twApi=twitter.Api(username=self.username, password=self.passwd)
      self.rss = readrss.parse(url)

    def twitIt(self, items):
        oldItems=pItems=0
        for it in list(items):
            txt=it["title"][0:114] +" "+tiny(it["link"])
            try:
                status = self.twApi.PostUpdate(txt)
                self.rss.updateLastRead(it)
                print "status: ", status.text
                time.sleep(5)
            except (BadStatusLine, HTTPError):
                #lets try in the nex ttime
                return

    def update(self):
        lastread = self.rss.getlastRead()
        if not lastread:
            self.twitIt(reversed(self.rss.feed['items'][:5]))
            self.rss.updateLastRead()
        else:
            lista = [item for item in self.rss.feed['items'] if item['updated_parsed'] > lastread]
            self.twitIt(reversed(lista[:5]))
            self.rss.updateLastRead()


def update():
    c = ConfigParser()
    configfile =os.path.expanduser('~/.feed2twitter/default.cfg')
    try:
        fd =  open(configfile, 'r')
    except IOError:
        print >>sys.stderr, "File %s not found" % configfile
        sys.exit(2)
    c.readfp(fd)


    url = c.get("global", "url").strip()
    username = c.get("global", "username").strip()
    password = c.get("global", "password").strip()


    feed2tw = Feed2Twitter(url,username,password)
    feed2tw.update()
