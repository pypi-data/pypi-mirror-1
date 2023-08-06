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

import urllib

def tiny(url):
    try:
        data = urllib.urlencode(dict(url=url, source="RSS2Twit"))
        encodedurl="http://www.tinyurl.com/api-create.php?"+data
        instream=urllib.urlopen(encodedurl)
        ret=instream.read()
        instream.close()

        if len(ret)==0:
            return url

        return ret

    except IOError, e:
      raise "urllib error."
