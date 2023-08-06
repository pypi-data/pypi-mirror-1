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
SooVee Serial Audio Manager - Intializes the graphical interface. It 
imports the interface from soovee.gui.main.

    - C{Exec(mode="podiobooks":str, optargs=[]:list) => None}
    - C{Login() => None}

@requires: L{wx}
@requires: L{soovee.lib.sv_read}
@requires: L{soovee.lib.sv_conf}
"""
import wx
import main as Gui #: Terminal interface module
import soovee.lib.sv_read as CACHEOBJ #: Web/file cache
from ..lib.sv_conf import USR_DATA, App_Data

#APP_DATA = None
#MODE = None


def Login():
    """
    Authorize serial audio user against service containing the feeds.
    
    @param userdata: USR_DATA persistent data object
    @type userdata: shelve object
    @requires: L{soovee.gui.main}
    """
    loginDlg = Gui.LoginDialog(parent=None, title="User Login", 
        description=(
            "Retrieve serial audio feeds for %s user." % APP_DATA['site']), 
        user=USR_DATA.get("user",""), 
        password=USR_DATA.get("password",""))
    loginDlg.SetIcon(Gui.app_icon())
    
    if loginDlg.ShowModal() == wx.ID_OK: 
        loginDlg.Destroy()
        user, password = loginDlg.Values()
        if user and password:
            query = {"handle": user, "password": password, "remember": "yes", 
                "Submit": "Log In"}
            try:
                if CACHEOBJ.Authorize(uri=APP_DATA['login'], query=query):
                    
                    return user, password
            except CACHEOBJ.CacheException as error:
                Login(text="Error: %s.\nRetrieve feed list for %s user." % (
                    error, APP_DATA['site']))

        Login(text="Login Failed.\nRetrieve feed list for %s user." % (
            APP_DATA['site']))

    else:
        loginDlg.Destroy()
        exit()

#
#{ Graphical interface initialization
#
def Exec(mode="podiobooks", optargs=None):
    """
    Authorize against a serial audio service account. Offer a login dialog to 
    enter user and password. Then intialize the main module of the gui interface
    to begin the process of feed preview. 
    
    @param mode: Service to retrieve serial audio info. Default 'podiobooks'
    @type mode: string
    @param optargs: Optional command line arguments passed.
    @type optargs: list
    @return:
    @rtype: None
    @requires: L{soovee.gui.main}
    """
    global APP_DATA
    MODE, APP_DATA = mode, App_Data(mode)
    Gui.APP_DATA = APP_DATA
    Gui.MODE = MODE

    App = wx.App()
    #
    #{ Get serial audio feed service account login
    #
    try:
        USR_DATA['user'], USR_DATA['password'] = Login()
    except CACHEOBJ.CacheException as errmsg:
        wx.MessageDialog(self, message=str(errmsg), 
            caption="Authorization Error", style=wx.OK | wx.ICON_ERROR)
        fileerror.ShowModal() # Shows it
        fileerror.Destroy() # finally destroy it when finished
        exit()
    except KeyboardInterrupt:
        exit()
    #
    #{ Show graphical interface
    #
    try:
        Gui.Window(cacheobj=CACHEOBJ, opmlpath=APP_DATA['opml'] % USR_DATA['user'])
        App.MainLoop()
    except KeyboardInterrupt:
        exit()
