#
# (c) 2009 Jeremy AustinBardo <tjaustinbardo AT gmail DOT com>
# Special thanks Marius Gedminas <marius AT gedmin DOT as> for his suggestions.
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
SooVee Serial Audio Manger - Feed elements module for the graphical inface. It 
handles a displaying element of the interface concerning feeds.

    - C{except UserCancel("Progress Dialog canceled."):}
    - C{ViewHtml(parent:object) -> None}
    - C{ViewHtml.OnLinkClicked(link:object) -> None}
    - C{CoverImg(parent:object) -> None}
    - C{ListCtrl(parent:object) -> None}
    - C{UpdateBttn(parent:object) -> None}
    - C{DownloadBttn(parent:object) -> None}

@newfield announce: Announce with TRANSCIEVER
@newfield response: Response for TRANSCIEVER
@newfield handle: Handle wx.Event

@requires: wx
@requires: wx.html
@requires: wx.lib.statbmp
@requires: wx.lib.pubsub
@requires: L{soovee.lib.sv_data}
@requires: L{soovee.gui.main}
@requires: L{soovee.conf}
"""

import wx, wx.html, wx.lib.pubsub as msg, wx.lib.statbmp as Cover
from soovee_lib.parse import Xml #: Opml / Rss data parsers
#from soovee.conf import CACHEDIR#, HOMEDIR #: Config data 

TRANSCIEVER = msg.Publisher() #: Interobject communication object.

SERVICE = None

#
#{ Feed Error Handler
#
class UserCancel(Exception):
    """
    Excption class to handle user cancel of a dialog.

        - C{except UserCancel, "Progress Dialog canceled.":}
    """

    def __init__(self, value):
        """
        Store exception message passed in except statement

        @param value: string
        @type value: exception message
        @return:
        @rtype: None
        """
        Exception.__init__(self, value)
        self.value = value

    def __str__(self):
        """
        Return exception instance of UserCancel

        @return: UserCancel instance
        @rtype: Exception
        """
        return repr(self.value)


def errordlg (parent, title, message):
    """
    Error Dialog to show error messages within the graphical interface.
    @param parent: parent wx.Window object
    @type parent: object
    @param title: dialog title
    @type title: basestring
    @param message: message describing service login
    @type message: basestring
    @return:
    @rtype: None
    """
    from main import app_icon
    dlg = wx.MessageDialog(parent=parent, caption=title, message=str(message),
        style=wx.CANCEL | wx.ICON_ERROR)
    dlg.SetIcon(app_icon())
    dlg.ShowModal() # Shows it
    dlg.Destroy() # finally destroy it when finished



#
#{ Feed Viewer
#
class ViewHtml(wx.html.HtmlWindow):
    """
    Show user their chosen serial audio feed details using dynamic html
    content generated from its rss data.

        - C{ViewHtml(parent:object) -> None}
        - C{ViewHtml.OnLinkClicked(link:object) -> None}

    @response: C{FEED_CHOICE}
    @response: C{FEED_RFRESH}
    @announce: C{MEDIA_CHOICE}
    @announce: C{FEED_DATA}
    """
    def __init__(self, parent, cache, path):
        """
        Create a wx.Html.HtmlWindow to hold dynamic html content.

        @param parent: parent wx.Window object
        @type parent: object
        @return:
        @rtype: None
        """
        wx.html.HtmlWindow.__init__(self, parent, wx.ID_ANY)
        self.__cache = cache
        if "gtk2" in wx.PlatformInfo: 
            self.SetStandardFonts()
        
        # Set Opml data to avoid query for each feed choice
        try:
            self.opml = Xml.opml(self.__cache.Cache(path).data())

        except self.__cache.CacheException as errmsg:
            errordlg (self, 'Caching Error', errmsg)

        else:
            TRANSCIEVER.sendMessage("FEED_RFRESH", self.opml)

            # Compose html page for HtmlWindow
            self.__composepage()
        
            # Set signal reception
            TRANSCIEVER.subscribe(topic="FEED_CHOICE",
                 listener=self.__updatepage)
            TRANSCIEVER.subscribe(topic="FEED_RFRESH",
                listener=self.__updatefeed)

    def OnLinkClicked(self, link):
        """
        Pass clicked <a href> link in wx.Html.HtmlWindow to handler. Each
        link will be handled by soovee.gui.media or a web browser.

        @announce: C{MEDIA_CHOICE} -- 
            I{Url string of clicked audio file link}

        @param link: wx.Html.HtmlWindow link clicked event.
        @type link: object
        @return:
        @rtype: None
        """
        clickedurl = link.GetHref()

        if clickedurl.endswith("mp3"):
            TRANSCIEVER.sendMessage(topic="MEDIA_CHOICE", data=clickedurl)

        else:
            wx.LaunchDefaultBrowser(clickedurl)

    def __updatepage(self, message):
        """
        Update wx.Html.HtmlWindow dynamic HTML content with new feed choice.

        @response: C{FEED_CHOICE} --
            I{Index interger of soovee.lib.sv_data.Opml query}

        @param message: TRANSCIEVER object
        @type message: object
        @return:
        @rtype: None
        """
        if not message.data == -1: ### Idiosync -1 is msg on exit and refresh???
            self.__composepage(feedindex=int(message.data))

    def __updatefeed(self, message):
        """
        Update self.Opml to keep our feed choices current.

        @response: C{FEED_RFRESH} --
            I{Opml list value}
        @param message: TRANSCIEVER object
        @type message: object
        @return:
        @rtype: None
        """
        self.opml = message.data

    def __composepage(self, feedindex=None):
        """
        Compose dynamic HTML content for wx.Html.HtmlWindow using a choice
        from self.Opml to get feed data. If feedindex is unset, data is
        randomly selected.

        @announce: C{FEED_DATA} --
            I{Dictionary of useful feed Data.}

        @param feedindex: Index interger of soovee.lib.sv_data.Opml query
        @type feedindex: int
        @return:
        @rtype: None

        @requires: L{soovee.forms}
        @requires: random
        """
        from ..forms import FORMS as forms #: Form plugins system
        
        if feedindex == None:
            import random
            opml = random.choice(self.opml) #: Randomly selected feed

        else: 
            opml = self.opml[feedindex] #: Chosen feed by its index interger

        composer = forms.get(command="view")

        try:
            rss = Xml.rss(self.__cache.Cache(opml['xmlUrl']).data())
        except self.__cache.CacheException as error:
            errordlg (self, 'Caching Error', error)

        self.SetPage(composer.item(data=opml, feed=rss, service=SERVICE))
        del composer

        TRANSCIEVER.sendMessage(topic="FEED_DATA", data={
            'pageurl': opml['htmlUrl'], 
            'imageurl': rss['sum']['image']['url'],
            'encloseurl': [eps['enclosure']['url'] for eps in rss['eps']],
            'feedtitle': rss['sum']['title']
            })


#{ Feed Controls
class CoverImg(Cover.GenStaticBitmap):
    """
    Show user their selected serial audio feed's cover image.

        - C{CoverImg(parent:object) -> None}

    @response: C{FEED_DATA}
    """
    _pageurl = None

    def __init__(self, parent, cache):
        """
        Create a Cover.GenStaticBitmap to hold an image which could be cached
        local or retrieved from the internet.

        @handle: C{wx.EVT_LEFT_DOWN} --
            I{lambda expression to load feed url in default browser.}

        @param parent: parent wx.Window object
        @type parent: object
        @return:
        @rtype: None
        """
        self.__cache = cache
        Cover.GenStaticBitmap.__init__(self, parent, wx.ID_ANY,
            wx.EmptyImage(), size=(144, 212))
        self.Bind(event=wx.EVT_LEFT_DOWN, 
            handler=lambda x:wx.LaunchDefaultBrowser(self._pageurl))
        self.SetToolTip(wx.ToolTip("Click to visit feed's webpage"))

        TRANSCIEVER.subscribe(listener=self._update, topic="FEED_DATA")

    def _update(self, message):
        """
        Compose the feed cover image.

        @response: C{FEED_DATA} --
            I{Dictionary of useful Rss Data.}

        @param message: TRANSCIEVER object
        @type message: object
        @return:
        @rtype: None
        """
        if isinstance(message.data, dict):
            self._pageurl = message.data['pageurl']
            try:
                self.SetBitmap(bitmap=wx.BitmapFromImage(wx.ImageFromStream(
                    self.__cache.Cache(message.data['imageurl']).data("rb"))))

            except self.__cache.CacheException as errmsg:
                errordlg (self, 'Caching Error', errmsg)



class ListCtrl(wx.ListBox):
    """
    Show user their serial audio feed list of subscribed opml feeds.

        - C{ListCtrl(parent:object) -> None}

    @response: FEED_REFRSH
    @announce: FEED_CHOICE
    """
    def __init__(self, parent):
        """
        Create a wx.ListBox to iterate the subscribed feed listing.

        @handle: C{wx.EVT_LISTBOX} --
            I{Feed selection made.}
        @announce: C{FEED_CHOICE} --
            I{Index interger of Data.Opml query.}

        @param parent: parent wx.Window object
        @type parent: object
        @return:
        @rtype: None
        """
        wx.ListBox.__init__(self, parent=parent, size=(200, -1), choices=[])
        self.Bind(event=wx.EVT_LISTBOX, 
            handler=lambda x:TRANSCIEVER.sendMessage(
                topic="FEED_CHOICE", data=self.GetSelection()))

        #self.SetToolTip(wx.ToolTip("Select a Serial Audio Feed"))

        TRANSCIEVER.subscribe(topic="FEED_RFRESH", 
            listener=self._update)

    def _update(self, message):
        """
        Compose subscribed feed list from the results of soove.lib.sv_data.Opml
        query.

        @response: C{FEED_RFRESH} --
            I{None value}
        @param message: TRANSCIEVER object
        @type message: object
        @return:
        @rtype: None
        """
        self.Set(items=[SERVICE.PRETITLE.sub("", feed['title'])
                for feed in message.data])

