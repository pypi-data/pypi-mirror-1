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
SooVee Serial Audio Manager - Configuration library for SooVee. It stores and 
retrieves persistent user data accross application usage. It also provides a 
central location for important service specific data to enable it use on 
multiple services.

    - C{USR_DATA}
    - C{CONFIGDIR}
    - C{CACHEDIR}
    - C{App_Data}

@requires: xdg.BaseDirectory
@requires: shelve
@requires: ConfigParser
@requires: soovee.lib.sv_file

@note: Currently service specific App_Data uses ConfigParser conf file. It is 
unclear if this is the best approach. 
@note: Need to implement fall back for the lack of xdg library. 
"""
import xdg.BaseDirectory as _baseDir
import shelve
import ConfigParser
import sv_file as File #: File and directory munging library

#
#{ Special directories SooVee will use.
#
CONFIGDIR = File.os.path.join(_baseDir.xdg_config_home, "soovee")
CACHEDIR = File.os.path.join(_baseDir.xdg_data_home, "soovee")
#
#{ User specific data SooVee will use.
#
USR_DATA = shelve.open(File.setName(filename="usr", workstore=CONFIGDIR, 
    combine=True), protocol=1)
#
#{ Service specific data SooVee will use.
#
class App_Data(ConfigParser.SafeConfigParser):
    """
    Service data container. Reimplement ConfigParser.SafeConfigParser to provide
    default values for absence of config file and access via a dict interface.
    """
    _confname = File.setName(filename="app", workstore=CONFIGDIR, combine=True)
    _default = {
        "site": "Podiobooks.com", 
        "opml": "http://www.podiobooks.com/opml/subscriptions/%s/list.opml",
        "login": "http://www.podiobooks.com/login.php",
        "query": "http://www.podiobooks.com/account/subscriptions.php?%s", 
        "query-add-name": "addsubID",
        "query-del-name": "unsubID", 
        "query-one-name": "force",
        "query-all-name":  "forceall"
        }

    def __init__(self, mode):
        """
        Intialize service data for passed mode.
        """
        ConfigParser.SafeConfigParser.__init__(self)
        
        self._mode = mode
        if File.os.path.exists(self._confname):
            self.read(self._confname)

    def __getitem__(self, name):
        """
        Get service data item of passed name.
        """
        if self.has_option(self._mode, name):
            return self.get(self._mode, name)
        elif name in self._default:
            return self._default[name]
        return None

    def __setitem__(self, name, value):
        """
        Set service data item of passed name.
        """
        if not mode in self.sections():
            self.add_section(self._mode)
        self.set(self._mode, name, value)
        with open(self._confname, 'w') as conffile:
            self.write(conffile)

