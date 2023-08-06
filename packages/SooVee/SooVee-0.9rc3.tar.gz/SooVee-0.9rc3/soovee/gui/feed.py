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
SooVee Serial Audio Manger - Feed support module for the graphical inface. It 
handles a user's subscription data---displaying, updating, and downloading.

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
@requires: L{soovee.lib.sv_conf}
"""

import wx, wx.html, wx.lib.pubsub as msg, wx.lib.statbmp as Cover
import soovee.lib.sv_data as Data #: Opml / Rss data parsers
from main import OPMLPATH, CACHEOBJ, APP_DATA, REGEX, app_icon #: Get environs.
from ..lib.sv_conf import CACHEDIR #: Config data 

TRANSCIEVER = msg.Publisher() #: Interobject communication object.


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
        self.err_msg = value

    def __str__(self):
        """
        Return exception instance of UserCancel

        @return: UserCancel instance
        @rtype: Exception
        """
        return repr(self.err_msg)

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
    def __init__(self, parent):
        """
        Create a wx.Html.HtmlWindow to hold dynamic html content.

        @param parent: parent wx.Window object
        @type parent: object
        @return:
        @rtype: None
        """
        #global OPMLPATH
        wx.html.HtmlWindow.__init__(self, parent, wx.ID_ANY)
        if "gtk2" in wx.PlatformInfo: self.SetStandardFonts()
        # Set Opml data to avoid query for each feed choice
        self.Opml = Data.Opml(
            CACHEOBJ.Cache(pathname=OPMLPATH, filename=OPMLPATH.split("/")[-1],
            workstore=CACHEDIR).data() )
        # Compose html page for HtmlWindow
        self.__composepage()
        # Set signal reception
        TRANSCIEVER.subscribe(listener=self.__updatepage, topic="FEED_CHOICE")
        TRANSCIEVER.subscribe(listener=self.__updatefeed, topic="FEED_RFRESH")

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
            I{None value}
        @param message: TRANSCIEVER object
        @type message: object
        @return:
        @rtype: None
        """
        self.Opml = Data.Opml(
            CACHEOBJ.Cache(pathname=OPMLPATH, filename=OPMLPATH.split("/")[-1],
            workstore=CACHEDIR).data() )

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
        from ..forms import Forms #: Forms system with format plugins
        if feedindex == None:
            import random
            feed = random.choice(self.Opml) #: Randomly selected feed
        else: feed = self.Opml[feedindex] #: Chosen feed by its index interger
        composer = Forms.Get(command="view")
        rss = Data.Rss(CACHEOBJ.Cache(feed['xmlUrl'], REGEX.toRss(feed['title']),
                workstore=CACHEDIR).data())
        outHtml = composer.item(item=feed, feed=rss, rx=REGEX)
        TRANSCIEVER.sendMessage(topic="FEED_DATA",
            data={
            'pageurl':composer.pageUrl, 'imageurl':composer.imageUrl,
            'encloseurl':composer.encloseUrls, 'feedtitle':composer.feedTitle
            })
        self.SetPage("".join(outHtml))
        del composer

#
#{ Feed Controls
#
class CoverImg(Cover.GenStaticBitmap):
    """
    Show user their selected serial audio feed's cover image.

        - C{CoverImg(parent:object) -> None}

    @response: C{FEED_DATA}
    """

    def __init__(self, parent):
        """
        Create a Cover.GenStaticBitmap to hold an image which could be cached
        local or retrieved from the internet.

        @param parent: parent wx.Window object
        @type parent: object
        @return:
        @rtype: None
        """
        Cover.GenStaticBitmap.__init__(self, parent, wx.ID_ANY,
            wx.EmptyImage(), size=(144,212))
        self.Bind(event=wx.EVT_LEFT_DOWN, handler=self.__clickimage)
        self.SetToolTip(wx.ToolTip("Click to view Podiobook webpage"))
        TRANSCIEVER.subscribe(listener=self.__updatefeed, topic="FEED_DATA")

    def __updatefeed(self, message):
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
            #regex = RegEx.Get(MODE)
            self.__pageUrl = message.data['pageurl']

            image = CACHEOBJ.Cache(pathname=message.data['imageurl'],
                filename=REGEX.PREIMAGEURL.sub("", message.data['imageurl']),
                workstore=CACHEDIR).data("rb")
            self.SetBitmap(bitmap=wx.BitmapFromImage(wx.ImageFromStream(image)))

    def __clickimage(self, event):
        """
        Open web browser to visit feed's html web page.

        @handle: wx.EVT_LEFT_DOWN on self
        @param event: wx.Event object
        @type event: object
        @return:
        @rtype: None
        """
        wx.LaunchDefaultBrowser(self.__pageUrl)


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

        @param parent: parent wx.Window object
        @type parent: object
        @return:
        @rtype: None
        """
        wx.ListBox.__init__(self, parent, wx.ID_ANY, size=(200,-1), choices=[])
        self.Bind(event=wx.EVT_LISTBOX, handler=self.__selectfeed)
        self.__updatefeed(None)
        #self.SetToolTip(wx.ToolTip("Select a Podiobook"))
        TRANSCIEVER.subscribe(listener=self.__updatefeed, topic="FEED_RFRESH")

    def __updatefeed(self, message):
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
        #global OPMLPATH
        #regex = RegEx.Get(MODE)
        self.Set(items=[
            REGEX.PRETITLE.sub("", feed['title'])
            for feed in Data.Opml(
                CACHEOBJ.Cache(OPMLPATH, OPMLPATH.split("/")[-1], 
                workstore=CACHEDIR).data()
                )
            ]
            )

    def __selectfeed(self, event):
        """
        Capture the selection of an individual feed.

        @handle: C{wx.EVT_LISTBOX} on self
        @announce: C{FEED_CHOICE} --
            I{Index interger of C{Data.Opml} query}
        @param event: wx.Event object
        @type event: object
        @return:
        @rtype: None
        """
        TRANSCIEVER.sendMessage(topic="FEED_CHOICE", data= self.GetSelection())

class UpdateBttn(wx.Button):
    """
    Feed control to allow a user to update their subscribed feeds.

        - C{PbUpdateBttn(parent:object) -> None}

    @announce: C{FEED_REFRSH}
    """

    def __init__(self, parent):
        """
        Create a wx.Button to signal an update action.

        @param parent: parent wx.Window object
        @type parent: object
        @return:
        @rtype: None
        """
        wx.Button.__init__(self, parent, wx.ID_ANY,
            label="Update Subscriptions", size=(200, -1))
        self.Bind(event=wx.EVT_BUTTON, handler=self.__updatefeed)
        #self.SetToolTip(wx.ToolTip("Click to Update Podiobook subscriptions"))

    def __updatefeed(self, event):
        """
        Enable a user to update their subscribed serial audio feeds.

        @handle: C{wx.EVT_BUTTON} on self
        @announce: C{FEED_REFRSH} --
            I{None value}
        @param event: wx.Event object
        @type event: object
        @return:
        @rtype: None
        """
        #global OPMLPATH
        #
        # Update OPML data
        #
        Opml = Data.Opml(
            CACHEOBJ.Cache(OPMLPATH, OPMLPATH.split("/")[-1], 
            workstore=CACHEDIR, update=True).data()
            )
        #
        # Show wx.ProgressDialog to track update progress
        #
        dialog = wx.ProgressDialog ( 'Updating serial audio content.',
            'Please, wait while cached feeds are updated.',
            maximum=len(Opml),
            style=wx.PD_APP_MODAL|wx.PD_AUTO_HIDE|wx.PD_CAN_ABORT)
        #
        # Update Rss data
        #
        prog_count = 1
        for feed in Opml:
            checkReturn = dialog.Update(
                prog_count, REGEX.PRETITLE.sub("", feed['title'])
                )
            if not checkReturn[0]: break #: Monitor for user cancel
            # Pull only those serial audio feeds which have not ended
            filename = REGEX.toRss(feed['title'])
            rssFile = Data.Rss(CACHEOBJ.Cache(pathname=feed['xmlUrl'], 
                    filename=filename, workstore=CACHEDIR).data())
            if not rssFile['eps'][-1].get('description',"") == "The End":
                CACHEOBJ.Cache(pathname=feed['xmlUrl'], filename=filename, 
                    workstore=CACHEDIR, update=True)
            prog_count += 1
        dialog.Destroy()
        TRANSCIEVER.sendMessage("FEED_RFRESH", None)


class DownloadBttn(wx.Button):
    """
    Feed control to allow a user to download their serail audio feed enclosures.

        - C{DownloadBttn(parent:object) -> None}

    @response: C{FEED_DATA}
    """
    def __init__(self, parent):
        """
        Create a wx.Button to signal a download action.

        @param parent: parent wx.Window object
        @type parent: object
        @return:
        @rtype: None
        """
        wx.Button.__init__(self, parent, wx.ID_ANY, label="Download Episodes",
                    size=(200, -1))
        self.Bind(event=wx.EVT_BUTTON, handler=self.__downloadenclosure)
        #self.SetToolTip(wx.ToolTip("Click to download Podiobook Episodes"))
        TRANSCIEVER.subscribe(self.__updateenclosure, "FEED_DATA")

    def __updateenclosure(self, message):
        """
        Collect serial audio feed.data to enable retrieval of episodes.

        @response: C{FEED_DATA} --
            I{Dictionary of useful Rss Data.}
        @param message: TRANSCIEVER object
        @type message: object
        @return:
        @rtype: None
        """
        if isinstance(message.data, dict):
            self.__encloseUrls = message.data['encloseurl']
            self.__feedtitle = message.data['feedtitle']

    def __downloadenclosure(self, event):
        """
        Enable a user to download enclosures from subcribed serial audio feeds.

        @handle: C{wx.EVT_BUTTON} on self
        @param event: wx.Event object
        @type event: object
        @return:
        @rtype: None
        @requires: os
        """

        def report(blockread, blocksize, filesize):
            """
            Progress report hook to show audio file percentage recieved.

            @param blockread: interger
            @type blockread: blocks read so far
            @param blocksize: interger
            @type blocksize: size of block read
            @param filesize: interger
            @type filesize: total size of file
            @return:
            @rtype: None
            """
            totalsize  = float(blockread * blocksize)
            if totalsize < float(1048576): ## File is less than a Megabyte
                size = "%.0f kb" % toKB(totalsize)
            else: ## File is greater than a Megabyte
                size = "%.1f mb" % toMB(totalsize)
            checkReturn = progress.Update(prog_count, "Received %s of %s." % (
                size, filename))
            if not checkReturn[0]: raise UserCancel, "Download ended by user"

        import os
        #
        # Show file dialog to choose where to save audio files.
        #
        directory = wx.DirDialog (None,
            message='Directory to store serial audio episodes.',
            defaultPath=USR_DATA.get('xLastDir', os.environ['HOME']),
            style=wx.PD_APP_MODAL|wx.DD_DEFAULT_STYLE)
        directory.SetIcon(app_icon())
        if directory.ShowModal() == wx.ID_OK:
            USR_DATA['xLastDir'] = directory.GetPath()
            workstore = directory.GetPath()
        else: return None
        directory.Destroy()
        #
        # Show progress dialog for audio file retrieval
        #
        progress = wx.ProgressDialog ( 'Fetching Serial Audio Episodes.',
            'Please, wait while they are retrieved.',
            maximum=len(self.__encloseUrls),
            style=wx.PD_APP_MODAL|wx.PD_AUTO_HIDE|wx.PD_CAN_ABORT)
        progress.SetIcon(app_icon())
        prog_count = 0
        feedtitle = REGEX.toRss(self.__feedtitle)[:-4]
        #
        # Retrieve each enclosure with soove.lib.sv_read
        #
        for url in self.__encloseUrls:
            urlObj = REGEX.LASTTWO.match(url)
            filename = "%s/%s"%(feedtitle, urlObj.group(2))
            try: # Retrieve feed audio file
                contents = CACHEOBJ.Cache(pathname=message.data['imageurl'], 
                    filename=REGEX.PREIMAGEURL.sub("", message.data['imageurl']),
                    data=False, hook=report, workstore=workstore)
            except UserCancel:
                progress.Destroy()
                break
            except CACHEOBJ.CacheException as errmsg:
                fileerror = wx.MessageDialog(self, message=str(errmsg), 
                    caption="Download Error", style=wx.OK | wx.ICON_ERROR)
                fileerror.ShowModal() # Shows it
                fileerror.Destroy() # finally destroy it when finished
                progress.Destroy()
                break
            
            prog_count += 1
        #
        # Format an m3u playlist Forms
        #
        composer = Form.Compose(command="m3u",formtype="enc")
        composer.write(("%s/%s.m3u" % (feedtitle, feedtitle)), workstore,
            self.__encloseUrls)
        progress.Destroy()
