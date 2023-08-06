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
SooVee Serial Audio Manager - Plugin loader library for Soovee. This loads or 
lists a plugin extension to add additional function. 

    - C{loadMod(modprefix:str, directory:str, filesuffix:str) -> None}
    - C{loadMod.Get(methodvalue:str) -> object}
    - C{loadMod.List() -> list}

"""

class loadMod(object):
    """
    Provides a simple plugin extension import object.
    
        - C{loadMod.Get(methodvalue:str) -> object}
        - C{loadMod.List() -> list}
    """

    def __init__(self, modprefix, directory, filesuffix):
        """
        Create a list of modules in the directory passed with the filesuffix 
        passed. modprefix passed is string format that builds the final import
        path with the files discovered. Ingnores files prepended with '_'.
        
        @param modprefix: Prefix import of methods to load.
        @type modprefix: basestring
        @param directory: File list of which directory.
        @type directory: basestring
        @param filesuffix: Suffix for files that to load methods.
        @type filesuffix: basestring
        @return: List of available methods.
        @rtype: list
        @requires: os
        """
        import os
        self._modsavail = [
            __import__(modprefix % filename[:-3], None, None, [''])
            for filename in os.listdir(directory)
            if filename.endswith(filesuffix) and not filename.startswith('_')
            ]

    def Get(self, methodvalue):
        """
        Get the module that matches the methodvalue passed.

        @param methodvalue: method value presented with C{loadMod.List()}.
        @type methodvalue: basestring
        @return: matching format module object
        @rtype: object
        @raises ImportError: If methodvalue not found.
        """
        try:
            return [module for module in self._modsavail 
                if module.method == methodvalue][0]
        except IndexError:
            raise ImportError


    def List(self):
        """
        List available modules. Provides a list of commands to pass to Get() 
        to load a specific module.

        @return: modules listing
        @rtype: list
         """
        return [module.METHOD for module in self._modsavail]

