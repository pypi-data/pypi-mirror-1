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
SooVee Serial Audio Manger - Podiobooks transforms for serial audio feeds. These
are unique attributes for Podiobooks serial audio feed service.

    - C{SERVICE:str}: Name that identifies file.
    - C{SITENAME:str}: Name that identifies service.
    - C{OPMLURI:str}: URI for account provided opml feed on a service.
    - C{LOGINURI:str}: URI for login page to access account on a service.
    - C{QUERYURI:str}: URI for for performing account queries on a service.
    - C{QUERYNAME:dict}: Names for performing account actions on a service.
    - C{PRETITLE:re}: Remove 'Podiobooks.com:' from a string.
    - C{PRESUMMARY:re}: Remove 'In this podiobook:' from a string.
    - C{PREEPISODE:re}: Remove '-In this episode:' from a string.
    - C{PREIMAGEURL:re}: Remove 'http://www.podiobooks.com/images/' from string.
    - C{toRss(t:str) -> basestring}: Create local filename for a Rss feed.
    - C{mkAuth(u:str, p:str) -> dict}: Create login post query to perform.

@requires: re
@requires: soovee.conf.common
"""
import re
from common import DELSPACES

#{Service file name minus '.py'
SERVICE = "podiobooks"

#{ Service attributes
SITENAME = "Podiobooks.com"
OPMLURI = "http://www.podiobooks.com/opml/subscriptions/%s/list.opml"
LOGINURI = "http://www.podiobooks.com/login.php"
QUERYURI = "http://www.podiobooks.com/account/subscriptions.php?%s"
QUERYNAME = {
    "add": "addsubID",
    "del": "unsubID",
    "one": "force",
    "all": "forceall"
    }

#{ Service regular expressions
PRETITLE = re.compile("^Podiobooks.com: ")
PRESUMMARY = re.compile("^In this podiobook: ")
PREEPISODE = re.compile("^-In this episode: ")
PREIMAGEURL = re.compile("^http://www.podiobooks.com/images/")

#{ Service lambda expressions
toRss = lambda t: "%s.rss" % (DELSPACES.sub("", PRETITLE.sub("", t)))
mkAuth = lambda u, p: {"handle": u, "password": p, "remember": "yes", 
    "Submit": "Log In"}



