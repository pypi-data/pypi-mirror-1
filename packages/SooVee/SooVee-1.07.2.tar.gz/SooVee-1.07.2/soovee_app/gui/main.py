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
@requires: wx.media
@requires: L{soovee_app.gui.feed}
@requires: L{soovee_app.gui.media}
@requires: L{soovee_app.gui.tool}
@requires: L{soovee_app.gui.menu}
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

def window(cache, service, account):
    """
    Create a wxPython graphical interface to a serial audio service account. 
    Parse and compose a display for that accounts serial audio feeds. Provide
    controls to update, download, and listen to serial audio episodes.

    @param cache: Initialized soovee_lib.cache object.
    @type cache: object
    @param service: Initialized soovee.conf.serviceConf object.
    @type service: object
    @param account: Intialized soovee.conf.Account shelf object.
    @type account: object/dict
    @return:
    @rtype: None
    @requires: L{soovee_app.gui.feed}
    @requires: L{soovee_app.gui.media}
    @requires: wx.media
    """
    opml = service.OPMLURI % account['user']

    import wx.media as Play

    import feed as Feed, media as Media, tool as Tool, menu as Menu

    Media.SERVICE = Feed.SERVICE = service

    frame = wx.Frame(None, wx.ID_ANY, title="SooVee Serial Audio Manager - "
        "View Feeds",
        size=(800, -1))

    #{ Setup Panel with BoxSizers for SooVee feed parts
    mainpanel = wx.Panel(parent=frame, id=wx.ID_ANY, size=(800, -1))
    download = Tool.Download(parent=mainpanel, cache=cache, service=service)
    update = Tool.Update(parent=mainpanel, cache=cache, service=service,
        opml=opml)
    frame.SetMenuBar(Menu.MENUBAR(frame, {"update": update.feeds, 
        "download": download.encls}))
    try:
        Media.MEDIAPLAYER = Play.MediaCtrl(mainpanel, wx.ID_ANY)
    except NotImplementedError:
        Media.MEDIAPLAYER = None
    mainsizer = wx.BoxSizer()

    #{ Create Sidebar controls in a wx.BoxSizer
    leftcol = wx.BoxSizer(wx.VERTICAL)
    # Display a Rss feed's cover image
    leftcol.Add(item=Feed.CoverImg(parent=mainpanel, cache=cache), proportion=0,
        flag=wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, border=BORDER)
    # Display a caption for listened enclosure
    leftcol.Add(item=Media.MediaCptn(parent=mainpanel), proportion=0,
        flag=wx.EXPAND|wx.ALL, border=BORDER)
    # Display a slider to allow selecting listened enclosure position
    leftcol.Add(item=Media.PositionCtrl(parent=mainpanel), proportion=0,
        flag=wx.EXPAND|wx.ALL, border=BORDER)
    # Display a list of subscribed feeds to select
    leftcol.Add(item=Feed.ListCtrl(parent=mainpanel), proportion=6,
        flag=wx.EXPAND|wx.ALL, border=BORDER)
    # Display a button to allow pause/play of listened enclosure
    leftcol.Add(item=Media.ListenCtrl(parent=mainpanel), proportion=0,
        flag=wx.EXPAND|wx.ALL, border=BORDER)
    # Display a button to allow subscribed feed updates
    updatebttn = wx.Button(parent=mainpanel, label="Update Subscriptions", 
            size=(200, -1))
    updatebttn.Bind(event=wx.EVT_BUTTON, handler=update.feeds)
    leftcol.Add(item=updatebttn, proportion=0,
        flag=wx.EXPAND|wx.ALL, border=BORDER)
    # Display a button to allow download of a feed's enclosures
    downloadbttn = wx.Button(parent=mainpanel, label="Download Episodes",
            size=(200, -1))
    downloadbttn.Bind(event=wx.EVT_BUTTON, handler=download.encls)
    leftcol.Add(item=downloadbttn, proportion=0,
        flag=wx.EXPAND|wx.ALL, border=BORDER)
    # Place control sidebar sizer
    leftcol.SetMinSize(size=(210, -1))
    leftcol.SetSizeHints(frame)
    mainsizer.Add(item=leftcol, proportion=1, flag=wx.EXPAND, border=BORDER)
    # Create dynamic html viewer content based on feed's detail
    mainsizer.Add(item=Feed.ViewHtml(parent=mainpanel, cache=cache,
        path=opml), proportion=4, flag=wx.EXPAND, border=BORDER)
    mainsizer.SetSizeHints(frame)
    mainpanel.SetSizer(mainsizer)
    frame.Layout()
    frame.SetClientSize(mainpanel.GetBestSizeTuple())
    #
    # Add an icon for the application window
    #
    frame.SetIcon(app_icon())

    #
    # Show elements added to window
    #
    frame.Centre()
    frame.Show(True)

