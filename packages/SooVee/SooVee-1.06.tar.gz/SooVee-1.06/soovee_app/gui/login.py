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
SooVee Serial Audio Manager - Login support module for the graphical interface. 
It allows SooVee to authorize itself with a service account.

    - C{doAuthorize(service:obj, account:obj, err:str="") -> tuple}
    - C{LoginDialog(parent:object, title:str, description:str) -> None}
    - C{LoginDialog.GetValues(None) -> list}
    
@requires: wx
@requires: L{soovee.lib.sv_read}
@requires: L{soovee.gui.main}
"""
import wx
import main

BORDER = 3

def doauthorize(service, account, err=""):
    """
    Authorize serial audio user against service containing the feeds.
    
    @param service: Initialized soovee.conf.serviceConf object.
    @type service: object
    @param account: Intialized soovee.conf.Account shelf object.
    @type account: object/dict
    @param err: Error string to append to text description presented
    @type err: str
    @returns: tuple of cache, user, password that was accepted
    @rtype: tuple
    """
    import soovee_lib.cache as cache
    dlg = LoginDialog(parent=None, title="User Login", 
        description=("%sRetrieve serial audio feeds for %s user." % (
        err, service.SITENAME)), user=account.get("user",""),
        password=account.get("password",""))
    dlg.SetIcon(main.app_icon())
    
    if dlg.ShowModal() == wx.ID_OK: 
        dlg.Destroy()
        user, password = dlg.values()
        if user and password:
            try:
                if cache.authcookie(
                    uri=service.LOGINURI, query=service.MKAUTH(user, password)):
                    return cache, user, password
            except cache.CacheException as error:
                pass

        else:
            error = "User and password not valid."

        doauthorize(service, account, err="Error: %s.\n" % error)

    else:
        dlg.Destroy()
        exit()


class LoginDialog(wx.Dialog):
    """
    Show a wx.Dialog to recieve a user's name and password for a service.

        - C{LoginDialog(parent:object, title:str, description:str, user:str, 
            password:str) -> None}
        - C{LoginDialog.Values(None) -> list}
    """

    def __init__(self, parent, title, description, user, password):
        """
        Create and show a login dialog with a user and password entry.

        @param parent: parent wx.Window object
        @type parent: object
        @param title: dialog title
        @type title: basestring
        @param description: message describing service login
        @type description: basestring
        @param user: Current user name
        @type user: basestring
        @param password: Current password
        @type password: basestring
        @return:
        @rtype: None
        """
        wx.Dialog.__init__(self, parent=parent, title=title, 
            size=(300, 150), style=wx.DEFAULT_DIALOG_STYLE)
        #
        # Layout with wx.BoxSizer -- message
        #
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(item=wx.StaticText(self, wx.ID_ANY, label=description),
            proportion=0, flag=wx.ALIGN_CENTER|wx.EXPAND|wx.ALL, border=BORDER)
        #
        # Layout with wx.FlexGridSizer -- label and control
        #
        fg = wx.FlexGridSizer(rows=2, cols=2, vgap=(BORDER+BORDER), hgap=BORDER)
        fg.Add(item=wx.StaticText(self, wx.ID_ANY, label="User:"), proportion=0,
            flag=wx.ALIGN_RIGHT)
        userctrl = wx.TextCtrl(self, wx.ID_ANY, name="user")
        userctrl.SetValue(value=user)
        fg.Add(item=userctrl, proportion=9, flag=wx.EXPAND)
        fg.Add(item=wx.StaticText(self, wx.ID_ANY, label="Password:"),
            proportion=0, flag=wx.ALIGN_RIGHT)
        pswrdctrl = wx.TextCtrl(self, wx.ID_ANY, name="password",
            style=wx.TE_PASSWORD)
        pswrdctrl.SetValue(value=password)
        fg.Add(item=pswrdctrl, proportion=9, flag=wx.EXPAND)
        fg.AddGrowableCol(1)
        sizer.Add(item=fg, proportion=0, flag=wx.EXPAND|wx.ALL, border=BORDER)
        #
        # Layout with wx.StdDialogButtonSizer -- buttons
        #
        btns = wx.StdDialogButtonSizer()
        okay = wx.Button(self, wx.ID_OK)
        okay.SetDefault()
        btns.AddButton(okay)
        btns.AddButton(wx.Button(self, wx.ID_CANCEL))
        btns.Realize()
        sizer.Add(item=btns, proportion=0, flag=wx.EXPAND|wx.ALL, border=BORDER)
        self.SetSizer(sizer)

    def values(self):
        """
        Retrieve values set by login dialog.

        @return: [user, password]
        @rtype: list
        """
        return [self.FindWindowByName("user").GetValue(), 
            self.FindWindowByName("password").GetValue()]
