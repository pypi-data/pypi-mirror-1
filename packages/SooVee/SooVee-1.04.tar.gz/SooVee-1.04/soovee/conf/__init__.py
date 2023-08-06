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
SooVee Serial Audio Manger - Service Config plugin module for setting values. 
It provides common and service specific modifiers for the chosen interface.

    - C{HOMEDIR:str}
    - C{CONFIGDIR:str}
    - C{CACHEDIR:str}
    - C{serviceConf(service:str) -> None}
    - C{serviceConf.list(None) -> None}
    - C{Account:dict}

Conf Plugin Basic Design
==========================
    Common Attributes
    -----------------
    These are attributes common to all serial audio feed services. Loaded from 
    common.py and stored in serviceConf._common.
    - C{DELSPACES:re}
    - C{LASTTWO:re}
    - C{DELHTML:re}
    - C{toMB(x:float|int) -> float}
    - C{toKB(x:float|int) -> float}
    - C{getImages(d:str) -> basestring}
    - C{getLinks(d:str) -> basestring}

    Service Attributes
    ------------------
    These are unique attributes for a serial audio feed service. Loaded from 
    a file of its name and stored in serviceConf._service.
    
    - C{SERVICE:str}
    - C{SITENAME:str}
    - C{OPMLURI:str}
    - C{LOGINURI:str}
    - C{QUERYURI:str}
    - C{QUERYNAME:dict}
    - C{PRETITLE:re}
    - C{PRESUMMARY:re}
    - C{PREEPISODE:re}
    - C{PREIMAGEURL:re}
    - C{toRss(t:str) -> basestring}
    - C{mkAuth(u:str, p:str) -> dict}
    
@requires: xdg.BaseDirectory
@requires: os
@requires: shelve
@requires: soovee.lib.sv_file
"""
import os
import shelve
from ..lib.sv_file import setName #: File and directory munging library

def __setDirectories():
    """
    Assign Soovee's directories a path value. Attempt to get system defaults 
    with xdg.BaseDirectory module, otherwise set these as the user's home. Then 
    append these directories with 'soovee'.

    @requires: xdg.BaseDirectory
    @requires: os.eviron
    @requires: os.path
    """
    try:
        #{ Attempt to load xdg.basedirectory for xdg default directories
        from xdg.BaseDirectory import xdg_config_home as cache
        from xdg.BaseDirectory import xdg_data_home as config

    except ImportError:
        #{ Otherwise, assign the directory values as None
        cache, config = (None, None)

    home = os.environ['HOME']
    return (home, os.path.join(config or home, "soovee"), 
        os.path.join(cache or home, "soovee"))

HOMEDIR, CONFIGDIR, CACHEDIR = __setDirectories()

Account = shelve.open(setName(filename="usr", workstore=CONFIGDIR, 
    combine=True), protocol=1)

class serviceConf(object):
    """
    Common and Service related attributes for SooVee. Run time attributes are 
    common and service modules from the soovee.conf package. Possible service 
    modules to load can be determined with serviceConf.List().
    
        - C{serviceConf(service:str) -> None}
        - C{serviceConf.list(None) -> None}
    
    @requires: os
    """

    def __init__(self,service):
        """
        Load the run time attributes for SooVee from soovee.conf package modules
        common and passed service value.
        
        @param service: Name of service module to get runtime attributes.
        @type service: basestring
        @return:
        @rtype: None
        """
        self._common = __import__("soovee.conf.common", None, None, [''])
        self._service = __import__("soovee.conf.%s"%service, None, None, [''])

    def __getattr__(self, name):
        """
        Check for passed attribute name in stored service and common modules.
        
        @param service: Name of a runtime attribute.
        @type service: basestring
        @return: value of runtime attribute.
        @rtype: indetermined
        """
        if hasattr(self._service, name):
            return getattr(self._service, name)
        elif hasattr(self._common, name):
            return getattr(self._common, name)

    def List():
        """
        Check for passed attribute name in stored service and common modules.

        @return: Service modules available.
        @rtype: list
        """
        return [
            mod.SERVICE for mod in (
            __import__("soovee.conf.%s" % filename[:-3], None, None, [''])
            for filename in os.listdir(directory)
            if filename.endswith(filesuffix) and not filename.startswith('_')
            ) if hasattr(mod.SERVICE)
            ]
