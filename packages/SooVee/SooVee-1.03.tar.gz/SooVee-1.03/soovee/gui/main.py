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

@requires: wx
@requires: wx.lib.pubsub
@requires: L{soovee.gui.feed}
@requires: L{soovee.gui.media}
@requires: wx.media
"""
import wx, wx.lib.pubsub as msg

BORDER = 3
TRANSCIEVER = msg.Publisher() #: Interobject communication object.

def app_icon():
    """
    Set uniform application icon.
    @return: wx.Icon of pbparse-32.png
    @rtype: object
    """
    return wx.Icon("/usr/share/pixmaps/soovee-32.png",
        wx.BITMAP_TYPE_PNG)

def Window(cacheobj, service, account):
    """
    Create a wxPython graphical interface to a serial audio service account. 
    Parse and compose a display for that accounts serial audio feeds. Provide
    controls to update, download, and listen to serial audio episodes.

    @param cacheobj: Initialized soovee.lib.sv_read object.
    @type cacheobj: object
    @param service: Initialized soovee.conf.serviceConf object.
    @type service: object
    @param account: Intialized soovee.conf.Account shelf object.
    @type account: object/dict
    @return:
    @rtype: None
    @requires: L{soovee.gui.feed}
    @requires: L{soovee.gui.media}
    @requires: wx.media
    """
    global CACHEOBJ, OPMLPATH, Download, Update
    CACHEOBJ, OPMLPATH = (cacheobj, service.OPMLURI % account['user'])

    import wx.media as Play

    import feed as Feed, media as Media, tool as Tool
    Media.Service = Feed.Service = service
    #Media.TRANSCIEVER = Media.TRANSCIEVER = Tool.TRANSCIEVER = TRANSCIEVER
    window = wx.Frame(None, wx.ID_ANY, title="SooVee Serial Audio Manager - "
        "View Feeds",
        size=(800, -1))

    #
    #{ Setup Panel with BoxSizers for SooVee feed parts
    #
    MainPanel = wx.Panel(parent=window, id=wx.ID_ANY, size=(800, -1))
    Download = Tool.Download(parent=MainPanel, cache=CACHEOBJ, service=service)
    Update = Tool.Update(parent=MainPanel, cache=CACHEOBJ, service=service,
        opml=OPMLPATH)
    window.SetMenuBar(menubar(window))
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

class menubar(wx.MenuBar):

    def __init__(self, parent):
        wx.MenuBar.__init__(self)
        self.__parent = parent
        menu = [
            ('&Feeds', [
                ('&Update Subscriptions', Update.setFeeds, ""),
                ('&Download Episodes', Download.getEncls, ""),
                ('&Exit', lambda x:parent.Close(), ""),
            ]),
            ('&Help', [
                ('&About', self._about, ""),
            ])
        ]

        for title, subMenu in menu:
            self.Append(self._buildMenus(subMenu), title)

    def _buildMenus(self, subMenu):
        menuObj = wx.Menu()
        for item in subMenu:
            if not item: #allow now to add separators
                menuObj.AppendSeparator()
                continue
            _id = wx.NewId()
            if len(item) == 2 and isinstance(item[1], list):
                title, action = item
                menuObj.AppendMenu(_id, title, self._buildMenus(action))
            elif len(item) == 3 and isinstance(item[1], object):
                title, action, statustext = item
                menuObj.Append(_id, title, statustext)
                wx.EVT_MENU(self.__parent, _id, action)
        return menuObj

    def _about(self, event):
        description = ("Manage and perfom many tasks of your serial audio "
            "service account right from the desktop.View individual feeds; Play"
            " or download episodes; Update contents from your account.")
        licence = ("This program is free software; you can redistribute it "
            "and/or modify it under the terms of the GNU General Public License"
            " as published by the Free Software Foundation; version 2 only of "
            "the License.\r\n"
            "This program is distributed in the hope that it will be useful,"
            " but WITHOUT ANY WARRANTY; without even the implied warranty of "
            " MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the "
            " GNU General Public License for more details.\r\n"
            "You should have received a copy of the GNU General Public License"
            "along with this program; if not, write to the Free Software"
            "Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  "
            "02111-1307  USA")

        info = wx.AboutDialogInfo()

        info.SetIcon(wx.Icon("/usr/share/pixmaps/soovee-64.png",
            wx.BITMAP_TYPE_PNG))
        info.SetName('Soovee Serial Audio Manager')
        info.SetVersion('1.03')
        info.SetDescription(description)
        info.SetCopyright('(C) 2009 Jeremy Austin-Bardo')
        info.SetWebSite('http://soovee.ausimage.us')
        info.SetLicence(licence)
        info.AddDeveloper('Jeremy Austin-Bardo')
        info.AddDocWriter('Jeremy Austin-Bardo')
        info.AddArtist('Jeremy Austin-Bardo')

        wx.AboutBox(info)





