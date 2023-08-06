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
SooVee Serial Audio Manger - RegEx plugin module for selecting portions of data.
It modifies and extracts data from serial audio feed fields with regular 
expressions and lambdas.

    - C{RegEx.Get(service:str) -> object}
    - C{Regex.List() -> list}

Regex Plugin Basic Design
=========================
    Object Methods
    --------------
    - C{RegEx.toRss(str) -> str}
    - C{RegEx.toMB(int) -> str}
    - C{RegEx.toKB(int) -> str}
    Object Compiled RegEx's
    -----------------------
    - RegEx.PRETITLE
    - RegEx.PRESUMMARY
    - RegEx.PREEPISODE
    - RegEx.PREIMAGEURL
    - RegEx.IMGSOURCE
    - RegEx.DELSPACES
    - RegEx.LASTTWO
    - RegEx.DELHTML
    Object Attributes
    -----------------
    - C{RegEx.SERVICE = "service name"}

@requires: os
@requires: soovee.lib.sv_mods
@note: This package may change to better suit its intended purpose of providing
    service specific data to SooVee. Merge with other config data of same useage
    a possibility.
"""
import os
from ..lib.sv_mods import loadMod


class __regexMod(loadMod):
    """
    Reimplement loadMod module to provide a plugin extension loader object
    for modification methods of serial audio data. Get() and List() have been 
    modified to be specific for the regex plugin module.

        - C{__regexMod.Get(service:str) -> object}
        - C{__regexMod.List() -> list}
    """

    def Get(self, service):
        """
        Get the module that matches the service passed.

        @param service: Name of service to that is listed with C{regexMod.List()}
        @type service: basestring
        @return: matching regex plugin module.
        @rtype: object
        @raises ImportError: If there is no such format plugin module available.
        """
        try:    
            return [module for module in self._modsavail 
                if module.SERVICE == service ][0]
        except IndexError:
            raise ImportError

    def List():
        """
        List available modules Provides a list of services that can be passed
        to Get() to load a specific module.

        @return: matching regex modules RegEx.Service. Services available.
        @rtype: list
         """
        return [module.SERVICE for module in self._modsavail]

#{ Intialize regexMod that will create the RegEx access module.
RegEx = __regexMod(modprefix="soovee.regex.%s", 
    directory=os.path.dirname(__file__), filesuffix="regex.py")

