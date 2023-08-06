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
SooVee Serial Audio Manger - Podiobooks search page extraction for the pages 
plugin module. It will makes the extracted data available in an Opml style dict.

@requires: re
"""
import re

METHOD = ("all", "podiobooks")
TYPE = "htm"
PAGE = "podiobooks/search.php?showall=true"

#
#{ Html format for http://podiobooks.com/podiobooks/search.php
#
FORMAT = re.compile("<td width=\"60\" align=\"center\"><a href=\""
    "(?P<htmUrl>.*?)\"><img vspace=\"5\" hspace=\"5\" align=\"left\" src=\""
    "(?P<imgUrl>.*?)\" alt=\"(?:.*?)\"  border=0 /></a></td><td width=\"125\""
    "><b><a href=\"(?:.*?)\">(?P<title>.*?)</a></b><br /><span class=\""
    "smalltext\">(?P<author>.*?)</class></td><td>(?P<description>.*?)<br/>",
    re.DOTALL)

