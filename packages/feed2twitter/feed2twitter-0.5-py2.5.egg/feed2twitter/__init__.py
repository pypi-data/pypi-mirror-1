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
from options import Options
import readrss
import re
import time
from pprint import pprint
from tinyurl import tiny
from parsetime import parsetime
from httplib import BadStatusLine
from urllib2 import HTTPError

class Feed2Twitter(object):
    def __init__(self,  url, username, passwd, mode='title', items = 5):
        self.mode = mode
        self.url = url
        self.items = items
        self.username = username
        self.passwd = passwd
        self.twApi = twitter.Api(username=self.username, password=self.passwd)
        self.twApi.SetSource('feed2twitter')
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
                #lets try in the next time
                return

    def update(self):
        lastread = self.rss.getlastRead()
        if not lastread:
            self.twitIt(reversed(self.rss.feed['items'][:self.items]))
        else:
            try:
                lista = [item for item in self.rss.feed['items'] if item['published_parsed'] > lastread]
            except:
                lista = [item for item in self.rss.feed['items'] if item['updated_parsed'] > lastread]
            self.twitIt(reversed(lista[:self.items]))

def update():
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
    print(interval)
    while True:
        feed2tw = Feed2Twitter(url, username, password, mode, items)
        feed2tw.update()
        time.sleep(interval)
