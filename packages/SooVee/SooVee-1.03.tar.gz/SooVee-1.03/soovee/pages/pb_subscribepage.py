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
SooVee Serial Audio Manger - Podiobooks subscription page extraction for the 
pages plugin module. It will makes the extracted data available in an Opml style
dict.

    - C{assignData(matchobj:object) -> dict}

@requires: re
"""
import re

METHOD = ("sub", "podiobooks")
TYPE = "rss"
WEBSITE = "http://www.podiobooks.com"
PAGE = "account/subscriptions.php"

#
#{ Html format for http://podiobooks.com/account/subscriptions.php
#
FORMAT = re.compile("<div id=\"books\">(?:.*?)<a name=\"(?P<idNum>.*?)\">"
    "</a><table(?:.*?)><a href=\"(?P<htmUrl>.*?)\"><img src=\"(?P<imgUrl>.*?)"
    "\" alt=\"(?:.*?)\"(?:.*?)></a><br><p>(?P<feedStatus>.*?)</p><br><a"
    "(?:.*?)><img(?:.*?)></a><br><a(?:.*?)>Report a problem<br>with this "
    "title</a><br></td><td(?:.*?)><span class=\"booktitle\"(?:.*?)>"
    "(?P<title>.*?)</span> <span class=\"subtitle\">by (?P<author>.*?)</span>"
    "<br(?:.*?)><table><tr><td(?:.*?)><div(?:.*?)><h3(?:.*?)>(?:.*?)</h3>\t"
    "We\'ll send you one episode of the book at a time\, on a schedule you "
    "can customize\, until you(?P<relStatus>.*?)\.<table><tr><td(?:.*?)><b>"
    "Your personal feed\:</b> <a href=\"(?P<rssFeed>.*?)\">(?:.*?)</a></td>"
    "</tr>(?:.*?)<form (?:.*?)form><br>Current episode in feed\: Part "
    "(?P<curEps>.*?) of (?P<totEps>.*?)\.(?:.*?)<br/>(?:.*?)<br/><span "
    "class=\"error\"><b>(?P<curStatus>.*?)</b></span>(?:.*?)</div><table><tr>"
    "<td(?:.*?)><h3(?:.*?)>Traditional RSS Feed:</h3><small>All of the "
    "(?:.*?) in a standard feed.(?:.*?)</small></td></tr><td(?:.*?)><a "
    "href=\"(?P<altUrl>.*?)\">(?:.*?)</a></td>", re.DOTALL)

