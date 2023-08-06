#
# (c) 2009 Jeremy AustinBardo <tjaustinbardo AT gmail DOT com>
# Special thanks Marius Gedminas <marius AT gedmin DOT as> for his suggestions.
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
SooVee Serial Audio Manager - Feed support module for the command inface. It 
manages or formats serial audio feeds from a service.

    - C{update(opmlpath:str) -> None}
    - C{format(opmlpath:str, directory:str, format:str) -> None}
    - C{manage(action:str, idnum:int) -> None}
    
@requires: L{soovee.lib.sv_data}
@requires: L{soovee.cli.main}
@requires: L{soovee.lib.sv_conf}
"""

import soovee.lib.sv_data as Data #: Opml / Rss data parsers.
from main import CACHEOBJ, APP_DATA, REGEX #: Get current environment values.
from ..lib.sv_conf import CACHEDIR #: SooVee configuration values.

#
#{ Support methods for feed tasks
#
def update(opmlpath):
    """
    Update serial audio feeds for a service. Update the personal opml feed, then
    update each unfinished Rss feed subscribed by this account. Currently, feeds
    that contain an episode description of 'The End' are considered complete.

    @param opmlpath: Url path to Opml file for the account.
    @type opmlpath: basestring
    @return:
    @rtype: None
    """

    Opml = Data.Opml(
            CACHEOBJ.Cache(opmlpath, opmlpath.split("/")[-1], 
            workstore=CACHEDIR, update=True).data()
            )
            
    for feed in Opml:
        print "    * %(title)s." % feed
        try:
            rssFile = Data.Rss(CACHEOBJ.Cache(pathname=feed['xmlUrl'], 
                    filename=REGEX.toRss(feed['title']), 
                    workstore=CACHEDIR).data())
            if not rssFile['eps'][-1].get('description',"") == "The End":
                CACHEOBJ.Cache(pathname=feed['xmlUrl'], 
                    filename=REGEX.toRss(feed['title']), workstore=CACHEDIR, 
                    update=True)

        except CACHEOBJ.CacheException as error:
            print("CACHE ERROR: %s" % error)
        
    print("%(site)s subscriptions cache was updated." % APP_DATA)


def format(opmlpath, directory, format):
    """
    Format serial audio feeds for a service account. Load and parse serial audio
    feeds before using the option selected with the forms module.

    @param opmlpath: Url path to Opml file for the account.
    @type opmlpath: basestring
    @param directory: Directory to save new page format.
    @type directory: basestring
    @param format: soovee.forms module option.
    @type format: basestring
    @return:
    @rtype: None
    @requires: L{soovee.forms}
    """
    from ..forms import Forms #: Forms system with format plugins

    try: 
        composer = Forms.Get(command=format)
    except ImportError: 
        print("FORMS ERROR: Command not available.")

    else:
        try:
            composer.write(data=Data.Opml(CACHEOBJ.Cache(opmlpath, 
                opmlpath.split("/")[-1], workstore=CACHEDIR).data()),
                filename=composer.filename, workstore=None if directory == "~" 
                else directory, cache=Conf.CACHEDIR)
        
        except TypeError: 
            print("FORMS ERROR: Invalid Data found.")
        
        except CACHEOBJ.CacheException as error:
            print("CACHE ERROR: %s" % error)
        
        else:
            print("Serial audio feed details were written to %s." % (
                directory or "your home directory"))

def manage(action, idnum):
    """
    Manage serial audio feeds for a service account. Set the query value to the
    service id for the selected feed to pass by GET using soove.lib.sv_query. 
    
    These queries currently handle updating subscriptions and releasing of new 
    episodes on service like Podiobooks.

    @param action: soovee.lib.sv_query module option. Currently [add|del|one|all]
    @type action: basestring
    @param idnum: service id for a selected feed.
    @type idnum: int
    @return:
    @rtype: None
    @note: WRT Podiobooks [del|one|all] use one id and [add] a different id.
    @requires: L{soovee.lib.sv_query}
    """
    from ..lib.sv_query import Query

    if Query(cache=CACHEOBJ, service=APP_DATA, action=action, idnum=idnum):
        print("Serial audio subscription for %s were %s." % (idnum,
            "Updated" if action in ['add','del'] else "Released"))
    else:
        print("QUERY ERROR: Id %s invalid or Cache Error Occurred" % idnum, 
            "Please, ensure the numeric Id is correct.")
