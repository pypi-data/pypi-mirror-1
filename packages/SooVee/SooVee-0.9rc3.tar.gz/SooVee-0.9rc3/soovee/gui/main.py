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
SooVee Serial Audio Manager - Main support module for the graphical interface. 
It contains the main window and its dialog windows.

    - C{app_icon(None) -> object}
    - C{Main(opmlpath:str) -> None}
    - C{LoginDialog(parent:object, title:str, description:str) -> None}
    - C{LoginDialog.GetValues(None) -> list}

@requires: wx.
"""
import wx

BORDER = 3

def app_icon():
    """
    Set uniform application icon.
    @return: wx.Icon of pbparse-32.png
    @rtype: object
    """
    return wx.Icon("/usr/share/pixmaps/soovee-32.png",
        wx.BITMAP_TYPE_PNG)

def Window(cacheobj, opmlpath):
    """
    Create a wxPython graphical interface to a serial audio service account. 
    Parse and compose a display for that accounts serial audio feeds. Provide
    controls to update, download, and listen to serial audio episodes.

    @param cacheobj: Initialized soovee.lib.sv_read object
    @type cacheobj: object
    @param opmlpath: Url path to Opml file for the account.
    @type opmlpath: basestring
    @return:
    @rtype: None
    @requires: L{soovee.gui.feed}
    @requires: L{soovee.gui.media}
    @requires: wx.media
    """
    global CACHEOBJ, OPMLPATH, REGEX
    from ..regex import RegEx
    REGEX = RegEx.Get(MODE)
    CACHEOBJ, OPMLPATH = cacheobj, opmlpath
    import wx.media as Play
    import feed as Feed, media as Media

    window = wx.Frame(None, wx.ID_ANY, title="SooVee Serial Audio Player - "
        "View Feeds",
        size=(800, -1))
    #
    #{ Setup Panel with BoxSizers for Podiobooks feed parts
    #
    MainPanel = wx.Panel(parent=window, id=wx.ID_ANY, size=(800, -1))
    try:
        Media.MEDIAPLAYER = Play.MediaCtrl(MainPanel, wx.ID_ANY)
    except NotImplementedError:
        pass
    MainSizer = wx.BoxSizer()
    #
    #{ Create Sidebar controls in a wx.BoxSizer
    #
    leftColumn = wx.BoxSizer(wx.VERTICAL)
    # Display a Rss feed's cover image
    CoverImg = Feed.CoverImg(parent=MainPanel)
    leftColumn.Add(item=CoverImg, proportion=0,
        flag=wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, border=BORDER)
    # Display a caption for listened enclosure
    MediaCptn = Media.MediaCptn(parent=MainPanel)
    leftColumn.Add(item=MediaCptn, proportion=0,
        flag=wx.EXPAND|wx.ALL, border=BORDER)
    # Display a slider to allow selecting listened enclosure position
    PositionCtrl = Media.PositionCtrl(parent=MainPanel)
    leftColumn.Add(item=PositionCtrl, proportion=0,
        flag=wx.EXPAND|wx.ALL, border=BORDER)
    # Display a list of subscribed feeds to select
    ListCtrl = Feed.ListCtrl(parent=MainPanel)
    leftColumn.Add(item=ListCtrl, proportion=6,
        flag=wx.EXPAND|wx.ALL, border=BORDER)
    # Display a button to allow pause/play of listened enclosure
    ListenCtrl = Media.ListenCtrl(parent=MainPanel)
    leftColumn.Add(item=ListenCtrl, proportion=0,
        flag=wx.EXPAND|wx.ALL, border=BORDER)
    # Display a button to allow subscribed feed updates
    UpdateBttn = Feed.UpdateBttn(parent=MainPanel)
    leftColumn.Add(item=UpdateBttn, proportion=0,
        flag=wx.EXPAND|wx.ALL, border=BORDER)
    # Display a button to allow download of a feed's enclosures
    DownloadBttn = Feed.DownloadBttn(parent=MainPanel)
    leftColumn.Add(item=DownloadBttn, proportion=0,
        flag=wx.EXPAND|wx.ALL, border=BORDER)
    # Place control sidebar sizer
    leftColumn.SetMinSize(size=(210,-1))
    leftColumn.SetSizeHints(window)
    MainSizer.Add(item=leftColumn, proportion=1, flag=wx.EXPAND, border=BORDER)
    #
    # Create dynamic html viewer content based on feed's detail
    #
    ViewHtml = Feed.ViewHtml(parent=MainPanel)
    MainSizer.Add(item=ViewHtml, proportion=4, flag=wx.EXPAND, border=BORDER)
    MainSizer.SetSizeHints(window)
    MainPanel.SetSizer(MainSizer)
    window.Layout()
    window.SetClientSize(MainPanel.GetBestSizeTuple())
    #
    # Add an icon for the application window
    #
    window.SetIcon(app_icon())
    #
    # Show elements added to window
    #
    window.Centre()
    window.Show(True)


class LoginDialog(wx.Dialog):
    """
    Show a wx.Dialog to recieve a user's name and password for a service.

        - C{LoginDialog(parent:object, title:str, description:str) -> None}
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
        @return:
        @rtype: None
        """
        wx.Dialog.__init__(self, parent, wx.ID_ANY, title=title, size=(300,150),
        style=wx.DEFAULT_DIALOG_STYLE)
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

    def Values(self):
        """
        Retrieve values set by login dialog.

        @return: [user, password]
        @rtype: list
        """
        return [self.FindWindowByName("user").GetValue(), 
            self.FindWindowByName("password").GetValue()]
