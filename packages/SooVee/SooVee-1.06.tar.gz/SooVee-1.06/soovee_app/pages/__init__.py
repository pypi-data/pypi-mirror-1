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
SooVee Serial Audio Manger - Page plugin module for extracting data. It will 
provide a list of available plugin modules and then makes the extracted data 
available.

    - C{Pages.Get(cacheobj:obj, page:str, update=True:bool) -> object}
    - C{Pages.List() -> list}

Page Plugin Basic Design
========================
    Object Attributes
    -----------------
    - C{Pages.METHOD = ("page nickname","service mode"):str}
    - C{Pages.PAGE = "service page url":str}
    - C{Pages.WEBSITE = "service base url":str}
    Object Compiled RegEx's
    -----------------------
    - C{Pages.FORMAT}

@requires: os
@requires: urlparse
@requires: L{soovee.lib.sv_mods}
@requires: L{soovee.conf}
@note: Some values should be relocated to the service configuration.
"""
import soovee.lib.sv_mods as mod
from urlparse import urljoin

class _Page(mod.Loader):
    """
    Reimplement loadMod module to provide a plugin extension that returns the
    extracted page data. The extraction will create Opml style dict value from 
    the plugin specified service page of serial audio info. Get() and 
    List() have been modified to be specific for the pages plugin module.

        - C{__pageMod.Get(cacheobj:obj, page:str, update=True:bool) -> object}
        - C{__pageMod.List() -> list}
    """

    def get(self, method, cache, service=None, update=True):
        """
        Extract the page data with the module that matches the Pages.METHOD.

        @param cacheobj: Initialized soovee.lib.sv_read.
        @type cacheobj: object
        @param page: Nickname for page to extract data.
        @type page: basestring
        @param update: Default 'True'. Force sv_read to load from the network.
        @type update: bool
        @return: Possible filename and Opml style dict.
        @rtype: str, dict
        @raises ImportError: If there is no such page plugin module available.
        """
        def mapping(items):
            """
            Extract data with passed re.match matchobj to create dictionary that
            is Opml style by its tag usage.

            @param matchobj: dictionary of match subgroups
            @type matchobj: dict
            @return: Opml-style dictionary of serial audio data
            @rtype: dict
            """
            return {
                #{ Fix relative urls from page in absolute
                'htmlUrl': urljoin(base=service.SITEURI, 
                    url=items.get("htmUrl", "")
                    ),
                'imgUrl': urljoin(base=service.SITEURI, 
                    url=items.get("imgUrl", "")
                    ),
                #{ Fix title and author to a single line
                'title': "%s by %s" % (
                    items.get("title", ""), 
                    items.get("author", "")
                    ),
                'description': items.get("description", None),
                #{ Fix status components into a single line
                'status': "%s %s/%s" % (
                    items.get("curStatus", ""), 
                    items.get("curEps", ""),
                    items.get("totEps", "")),
                'xmlUrl': items.get("rssFeed", None),
                'altUrl': items.get("altUrl", None),
                'subId': items.get("idNum", None),
                'type': parser.TYPE
            }
        if not hasattr(service,"SITEURI"):
            raise TypeError("Invalid service object pased to pages")

        parser = mod.Loader.get(self, (method, service.SERVICE))

        content = cache.Cache(
            urlpath=urljoin(base=service.SITEURI, url=parser.PAGE),
            update=update)

        return [mapping(match.groupdict()) 
            for match in parser.FORMAT.finditer(content.data())]

    def list(self, mode):
        """
        List available modules specific to current Service.SITENAME. Provides a 
        list of commands to pass to Get() to load a specific module.

        @return: modules listing
        @rtype: list
         """
        return [module.METHOD[0] for module in self._modsavail 
            if mode == module.METHOD[1]]


#{ Intialize pageMod that will create the Pages access module.
import os
PAGES = _Page(modprefix="soovee_app.pages.%s", 
    directory=os.path.dirname(__file__), filesuffix="page.py")

