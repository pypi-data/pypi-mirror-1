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

@requires: wx
@requires: L{soovee.conf}
@requires: L{soovee.gui.main}
@requires: L{soovee.gui.login}
"""
import wx
import login as Auth #: Graphical login module
import main as Gui #: Graphical interface module
import soovee.conf as Conf

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
    """
    Service = Conf.serviceConf(mode)
    Account = Conf.Account
    App = wx.App()

    try:
        #
        #{ Get authorized with serial audio feed service account.
        #
        CACHEOBJ, Account['user'], Account['password'] = Auth.doAuthorize(
        service=Service, account=Account)
        #
        #{ Show graphical interface
        #
        Gui.Window(cacheobj=CACHEOBJ, service=Service, account=Account)
        App.MainLoop()
    except KeyboardInterrupt:
        App.close()
        exit()
