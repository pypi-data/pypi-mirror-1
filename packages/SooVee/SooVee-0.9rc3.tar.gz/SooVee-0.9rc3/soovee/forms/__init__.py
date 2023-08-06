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
SooVee Serial Audio Manger - Format plugin module for creating pages. It will 
provide a list of available plugin modules and then makes that module available.

    - C{Forms.Get(command:str, formtype="frm":str) -> object}
    - C{Forms.List(formtype="frm":str) -> list}

Format Plugin Basic Design
==========================
Object Methods
--------------
    - C{Format.write(filename:str, workstore:str, data:list, cache=None:obj, 
        rx=None:obj) -> None}
    - C{Format.item(item:dict, feed={}:dict, rx=None:obj) -> None}

Object Attributes
-----------------
    - C{Format.method:tuple = (Type, Format) }
    - C{Format.filename:str = "save file name"}

@requires: os
@requires: L{soovee.lib.sv_mods}
"""
import os
from ..lib.sv_mods import loadMod


class __formMod(loadMod):
    """
    Reimplement loadMod module to provide a plugin extension loader object
    for formating methods of serial audio data. Get() and List() have been 
    modified to be specific for the forms plugin module.

        - C{__formMod.Get(command:str, formtype="frm":str) -> object}
        - C{__formMod.List(formtype="frm":str) -> list}
    """

    def Get(self, command, formtype="frm"):
        """
        Get the module that matches the C{Format.method} tuple. Build the 
        required tuple from command and formtype that are passed.

        @param command: 'Format' Name that is presented with formMod.List().
        @type command: basestring
        @param formtype: 'Type' of format. ['frm'|'htm'|'enc']. Default is"frm".
        @type formtype: basestring
        @return: Format plugin module that matches Format.method values passed.
        @rtype: object
        @raises ImportError: If there is no such format plugin module available.
        """
        try:
            return [module.Format() for module in self._modsavail 
                if module.Format.method == (formtype, command) ][0]
        except IndexError:
            raise ImportError

    def List(self, formtype="frm"):
        """
        List available modules for that match the passed formtype to the 
        Format.method first tuple entry. Provides a list of commands to pass
        to Get() to load a specific module.

        @param formtype: A format type ['frm'|'htm'|'enc']. Default is"frm".
        @type formtype: basestring
        @return: matching format modules Format.method[0]. Format commands.
        @rtype: list
         """
        return [module.Format.method[1] for module in self._modsavail
            if module.Format.method[0] == formtype]

#: Intialize formMod that will create the Forms access module.
Forms = __formMod(modprefix="soovee.forms.%s", 
    directory=os.path.dirname(__file__), filesuffix="format.py")

