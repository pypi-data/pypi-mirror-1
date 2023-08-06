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

    - C{browse(action:str, format:str, directory:str) -> None}
@requires: L{soovee.cli.main}
"""

from main import APP_DATA, REGEX, MODE, CACHEOBJ #: Get current environs.
from ..lib.sv_conf import USR_DATA

def browse(action, format, directory):
    """
    Extract serial audio info from a service's web page. Use soovee.pages to 
    then format a new page with soovee.forms of perhaps opml or html.

    @param action: soovee.pages option. Currently [sub|all].
    @type action: basestring
    @param format: soovee.forms option. Currently [html|opml].
    @type format: basestring
    @param directory: Directory to save new page.
    @type directory: basestring
    @return:
    @rtype: None
    @requires: L{soovee.pages}
    @requires: L{soovee.forms}
    """

    try:
        from ..pages import Pages #: Pages Module with web page parsers.
        print("%(site)s page is being read." % APP_DATA)
        #{ Read and extract data from selected service web page.
        opmldata = Pages.Get(cacheobj=CACHEOBJ, page=(action, MODE))

    except ImportError: 
        print("PAGE ERROR: Command not available.")

    except CACHEOBJ.CacheException as error:
        print("CACHE ERROR: Your page could not be read.", error)

    else:
        if opmldata:
            try:
                from ..forms import Forms #: Forms Module with data formaters.
                composer = Forms.Get(command=format, formtype="htm")
            except ImportError: 
                print("FORMAT ERROR: Command not available.")
            else:
                try:
                    #{ Format and write data from selected service web page.
                    composer.write(data=opmldata, 
                        filename=composer.filename % action,
                        workstore=None if directory == "~" else directory,
                        cache=CACHEOBJ, rx=REGEX)
                except TypeError: 
                    print("FORMAT ERROR: Invalid data found.")
                else:
                    print("Page details were written to "
                        "%s." % (directory or "your home directory"))

