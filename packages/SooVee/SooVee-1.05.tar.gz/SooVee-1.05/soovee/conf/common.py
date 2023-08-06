#
# (c) 2009 Jeremy AustinBardo <tjaustinbardo AT gmail DOT com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
"""
SooVee Serial Audio Manger - Common transforms for serial audio feeds. These are
attributes common to all serial audio feed services.

    - C{DELSPACES:re} - Remove all whitespace from a string
    - C{LASTTWO:re} - Remove all but the file and its parent from a path string.
    - C{DELHTML:re} - Remove all HTML / XML code from a string.
    - C{toMB(x:float|int) -> float} - Calculate megabytes from bytes
    - C{toKB(x:float|int) -> float} - Calculate kilobytes from bytes
    - C{getImages(d:str) -> basestring} - Find images in a HTML / XML string
    - C{getLinks(d:str) -> basestring} - Find links in a HTML / XML string

@requires: re
"""
import re

#{ Common regular expressions
DELSPACES = re.compile("[^\w]")
LASTTWO = re.compile("(.*)[\\/](.*)$")
DELHTML = re.compile("<.*?>")

#{ Common lambda expressions
toMB = lambda x: float(x) / 1048576
toKB = lambda x: float(x) / 1024
getImages = lambda d: re.compile("src=\"(.*?)\"").findall(d)
getLinks = lambda d: re.compile("href=\"(.*?)\"").findall(d)
