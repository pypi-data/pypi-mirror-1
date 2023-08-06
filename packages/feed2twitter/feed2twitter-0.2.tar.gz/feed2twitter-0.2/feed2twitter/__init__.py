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
import re
import time
from pprint import pprint
from tinyurl import tiny
from httplib import BadStatusLine
from urllib2 import HTTPError

class Feed2Twitter(object):
    def __init__(self,  url, username, passwd, mode='title'):
        self.mode = mode
        self.url=url
        self.username=username
        self.passwd=passwd
        self.twApi=twitter.Api(username=self.username, password=self.passwd)
        self.set_attr_headers()
        self.rss = readrss.parse(url)
    
    def set_attr_headers(self):
        return
        self.api.SetUserAgent('"feed2twitter/0.2"')
    

    def strip_tags(self,value):
        "Return the given HTML with all tags stripped."
        txt = re.sub(r'<[^>]*?>', '', value.replace('\t','').replace('\n','')) 
        return txt.replace('(Comments)','')

    def twitIt(self, items):
        oldItems=pItems=0
        for it in list(items):
            if self.mode == 'title':
                txt=it["title"][0:114] +" "+tiny(it["link"])
            elif self.mode == 'text':
                try:
                    txt = self.strip_tags(it.content[0].value)[0:140]
                except:
                    txt = self.strip_tags(it.summary)[0:140]
            else:
                txt = it['title'][0:144] + " " + tiny(it['link'])
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
        else:
            lista = [item for item in self.rss.feed['items'] if item['updated_parsed'] > lastread]
            self.twitIt(reversed(lista[:5]))

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
    mode = c.get("global","mode").strip()


    feed2tw = Feed2Twitter(url, username, password, mode)
    feed2tw.update()
