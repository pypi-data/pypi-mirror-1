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
SooVee Serial Audio Manger - Page support module for the command interface. It 
transforms web pages from a service with serial audio info into new formats.

    - C{browse(action:str, form:str, directory:str, cache:obj, service:obj) 
        -> None}

@requires: L{soovee_app.pages}
@requires: L{soovee_app.forms}
"""

#from main import CACHEOBJ, Service #, CACHEDIR #:Current Environs from Main.


def browse(action, form, directory, cache, service):
    """
    Extract serial audio info from a service's web page. Use soovee.pages to 
    then format a new page with soovee.forms of perhaps opml or html.

    @param action: soovee.pages option. Currently [sub|all].
    @type action: basestring
    @param format: soovee.forms option. Currently [html|opml].
    @type format: basestring
    @param directory: Directory to save new page.
    @type directory: basestring
    @param cache: Initialized soovee.lib.sv_read object.
    @type cache: object
    @param service: Initialized soovee.conf.serviceConf object.
    @type service: object
    @return:
    @rtype: None
    @requires: L{soovee_app.pages}
    @requires: L{soovee_app.forms}
    """

    try:
        from ..pages import PAGES as Pages #: Module to parse pages.
        print("%s page is being read." % service.SITENAME)
        #{ Read and extract data from selected service web page.
        opmldata = Pages.get(cache=cache, method=action, service=service)

    except ImportError: 
        print("PAGE ERROR: Command not available.")

    except cache.CacheException as error:
        print("CACHE ERROR: Your page could not be read.", error)

    else:
        if opmldata:
            try:
                from ..forms import FORMS as Forms #: Module to format data
                composer = Forms.get(command=form, form="htm")
            except ImportError: 
                print("FORMAT ERROR: Command not available.")
            else:
                try:
                    #{ Format and write data from selected service web page.
                    for item in composer.write(data=opmldata, 
                        filepath=composer.FILENAME % action,
                        workpath=None if directory == "~" else directory,
                        cache=cache, service=service):
                        print("Formatting feed: %s" % item)
                except TypeError: 
                    print("FORMAT ERROR: Invalid data found.")
                else:
                    print("Page details were written to "
                        "%s." % (directory or "your home directory"))

