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
SooVee Serial Audio Manager - Feed support module for the command interface. It 
manages or formats serial audio feeds from a service.

    - C{update(opml:str, cache:obj, service:obj) -> None}
    - C{compose(opml:str, directory:str, form:str, cache:obj, service:obj): 
        -> None}
    - C{manage(action:str, idnum:int, cache:obj, service:obj) -> None}
    
@requires: L{soovee_lib.ckuri}
@requires: L{soovee_app.forms}
@requires: L{soovee_lib.parse}
@requires: L{soovee_lib.mkuri}
"""

#
#{ Support methods for feed tasks
#
def update(opml, cache, service):
    """
    Update serial audio feeds for a service. Update the personal opml feed, then
    update each unfinished Rss feed subscribed by this account. Currently, feeds
    that contain an episode description of 'The End' are considered complete.

    @param opml: Url path to Opml file for the account.
    @type opml: basestring
    @param cache: Intialized soovee.lib.sv_read object. Default None.
    @type cache: obj
    @param service: Intialized soovee.regex object. Default None.
    @type service: obj
    @return:
    @rtype: None
    @requires: L{soovee_lib.ckuri}
    """
    from soovee_lib.ckuri import Refresh #: Feed update module

    try:
        #{ Update service account subscription data
        for index, title in (Refresh(cache=cache, opml=opml)):
            print "    * %s." % service.PRETITLE.sub("", title)

    except cache.CacheException as error:
        print("CACHE ERROR: %s" % error)

    print("%s subscriptions cache was updated." % service.SITENAME)


def compose(opml, directory, form, cache, service):
    """
    Format serial audio feeds for a service account. Load and parse serial audio
    feeds before using the option selected with the forms module.

    @param opml: Url path to Opml file for the account.
    @type opml: basestring
    @param directory: Directory to save new page format.
    @type directory: basestring
    @param form: soovee.forms module option.
    @type form: basestring
    @param cache: Intialized soovee.lib.sv_read object. Default None.
    @type cache: obj
    @param service: Intialized soovee.regex object. Default None.
    @type service: obj
    @return:
    @rtype: None
    @requires: L{soovee_app.forms}
    @requires: L{soovee_lib.parse}
    """
    from ..forms import FORMS as Forms #: Forms package with format plugins
    from soovee_lib.parse import Xml #: Opml / Rss data parsers.
    try: 
        #{ Set Forms Composer
        composer = Forms.get(command=form)
    except ImportError: 
        print("FORMS ERROR: Command not available.")

    else:
        try:
            #{ Write serial audio date with Forms Composer
            for item in composer.write(data=Xml.opml(cache.Cache(opml).data()),
                filename=composer.FILENAME, workstore=(cache.HOMEDIR 
                if directory == "~" or not directory else directory),
                cache=cache, service=service):
                print("Formatting feed: %s" % item)

        except TypeError as error: 
            print(error)
        
        except cache.CacheException as error:
            print("CACHE ERROR: %s" % error)
        
        else:
            print("Serial audio feed details were written to %s." % (
                directory or "your home directory"))

def manage(action, idnum, cache, service):
    """
    Manage serial audio feeds for a service account. Set the query value to the
    service id for the selected feed to pass by GET using soove.lib.sv_query. 
    
    These queries currently handle updating subscriptions and releasing of new 
    episodes on service like Podiobooks.

    @param action: soovee.lib.sv_query module option. Currently [add|del|one|all]
    @type action: basestring
    @param idnum: service id for a selected feed.
    @type idnum: int
    @param cache: Intialized soovee.lib.sv_read object. Default None.
    @type cache: obj
    @param service: Intialized soovee.regex object. Default None.
    @type service: obj
    @return:
    @rtype: None
    @note: WRT Podiobooks [del|one|all] use one id and [add] a different id.
    @requires: L{soovee_lib.mkuri}
    """
    from soovee_lib.mkuri import mkquery
    try:
        cache.Cache(mkquery(service, action, idnum.strip()), update=True)
        print("Serial audio subscription for %s were %s." % (idnum,
            "Updated" if action in ['add','del'] else "Released"))

    except KeyError:
        print("QUERY ERROR: Invalid query selection")
    
    except cache.CacheException as error:
        print("READ ERROR: %s" % error)
