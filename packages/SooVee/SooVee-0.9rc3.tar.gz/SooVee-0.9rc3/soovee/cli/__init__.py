#!/usr/bin/python
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
SooVee Serial Audio Manager - Intializes the command interface.

    - C{Exec(mode="podiobooks":str, optargs=[]:list) => None}

@requires: L{soovee.lib.sv_read}
@requires: L{soovee.lib.sv_conf}
"""
import soovee.lib.sv_read as CACHEOBJ #: Web/file cache
from ..lib.sv_conf import USR_DATA, App_Data

def Login():
    """
    Authorize serial audio user against service containing the feeds.
    
    @param userdata: USR_DATA persistent data object
    @type userdata: shelve object
    @requires: L{soovee.cli.main}
    """
    from main import LoginEntry
    user, password = USR_DATA.get("user",""), USR_DATA.get("password","")
    while 1:
        print("Authorizing with %(site)s." % APP_DATA)
        if user and password:
            query = {"handle": user, "password": password, "remember": "yes", 
                    "Submit": "Log In"}
            if CACHEOBJ.Authorize(uri=APP_DATA['login'], query=query):
                return (user, password)
            else:
                if raw_input(
                    "Relogin into %(site)s account? yes [no]" % APP_DATA
                    ).lower() == "yes":
                    user, password = LoginEntry(user, password)
                else:
                    exit()
        else:
            print("Login into a %(site)s account." % APP_DATA)
            user, password = LoginEntry(user, password)

#
#{ Command interface initialization
#
def Exec(mode="podiobooks", optargs=[]):
    """
    Authorize against a serial audio service account. Then intialize the main
    module of the command interface to begin the process of task selection.
    
    @param mode: Service to retrieve serial audio info. Default 'podiobooks'
    @type mode: string
    @param optargs: Optional command line arguments passed.
    @type optargs: list
    @return:
    @rtype: None
    @requires: L{soovee.cli.main}
    """
    global APP_DATA, MODE, USR_DATA, CACHEOBJ
    MODE, APP_DATA = mode, App_Data(mode) #:Setup SooVee for a specific Service.
    import main as Term #: Terminal interface module
    #
    #{  Get serial audio feed service account login
    #
    try:
        USR_DATA['user'], USR_DATA['password'] = Login()
    except CACHEOBJ.CacheException as error:
        print("Error: %s." % error)
        exit()
    except KeyboardInterrupt:
        exit("\n\nProgram terminated")
    #
    #{ Load command interface
    #
    try:
        Term.Main(cacheobj=CACHEOBJ, 
            opmlpath=APP_DATA['opml'] % USR_DATA['user'],
            command=optargs[0] if optargs else [])
    except KeyboardInterrupt:
        exit("\n\nProgram terminated")


