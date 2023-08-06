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
SooVee Serial Audio Manger- Feed support module for the graphical inface. It 
handles a user's subscription data---updating, and downloading.

@newfield announce: Announce with TRANSCIEVER
@newfield response: Response for TRANSCIEVER
@newfield handle: Handle wx.Event
"""
import wx , wx.lib.pubsub as msg
import feed
import main
from ..conf import CACHEDIR, HOMEDIR, Account

TRANSCIEVER = msg.Publisher() #: Interobject communication object.


class Update(object):

    def __init__(self, parent, cache, service, opml):
        """
        Initialize a download of serial audio feed enclosures. 
        
        @param parent: parent wx object.
        @type parent: object
        @param cache: Initialized soovee.lib.sv_read object.
        @type cache: object
        @param service: Initialized soovee.conf.serviceConf object.
        @type service: object
        @param opml: Service account opml uri
        @type opml: basestring
        @return: 
        @rtype: None
        """
        self._parent = parent
        self._cache = cache
        self._service = service
        self._opml = opml
        #TRANSCIEVER.subscribe(topic="UPDATE", listener=self.setFeeds)

    def setFeeds(self, message=None):
        """
        Update account subscribed serial audio feeds.

        @response: C{_UPDATE}
        @announce: C{FEED_RFRESH} -- 
                I{New Opml list data for consumption}

        @return: 
        @rtype: None
        @requires: soovee.lib.sv_check
        """
        from ..lib.sv_check import Feed as Refresh
        try:
            # Update serial audio feed list by passing opmlpath to feed
            opmldata = Refresh(cache=self._cache, opml=self._opml, 
                store=CACHEDIR, service=self._service)

            # Show wx.ProgressDialog to track update progress
            progressDlg = wx.ProgressDialog (
                parent=self._parent, title="Updating serial audio content.",
                message="Please, wait while cached feeds are updated.",
                maximum=len(opmldata),
                style=wx.PD_APP_MODAL|wx.PD_AUTO_HIDE|wx.PD_CAN_ABORT)
            progressDlg.SetIcon(main.app_icon())

            # Update Rss data by iterating new feed list
            for index, title in opmldata:
                checkReturn = progressDlg.Update(index, 
                    self._service.PRETITLE.sub("", title))
                if not checkReturn[0]: break #: Monitor for user cancel

        except self._cache.CacheException as errmsg:
            feed.errorDlg (parent=parent, title='Caching Error', message=errmsg)

        progressDlg.Destroy()
        TRANSCIEVER.sendMessage(topic="FEED_RFRESH", data=opmldata.opml)



class Download(object):
    """
    Download serial audio feed enclosures from a service account. Monitor
    TRANSCIEVER for 'FEED_DATA' to collect feed title and enclosures.
        
        - C{Download(parent:obj, cache:obj, service:obj) -> None}
        - C{Download.getEncls(None) -> None}
        
    @response: C{FEED_DATA}
    """
    def __init__(self, parent, cache, service):
        """
        Initialize a download of serial audio feed enclosures. 
        
        @param parent: parent wx object.
        @type parent: object
        @param cache: Initialized soovee.lib.sv_read object.
        @type cache: object
        @param service: Initialized soovee.conf.serviceConf object.
        @type service: object
        @return: 
        @rtype: None
        """
        self._parent = parent
        self._cache = cache
        self._service = service
        TRANSCIEVER.subscribe(topic="FEED_DATA", listener=self._set)
        #TRANSCIEVER.subscribe(topic="DOWNLOAD", listener=self.getEncls)

    def _set(self, message):
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
            self._encls = (message.data['feedtitle'], message.data['encloseurl'])

    def getEncls(self, message=None):
        """
        Download serial audio feed enclosures from a service account to user
        chosen location with visual feedback of progess

        @return:
        @rtype: None
        @requires soovee.forms
        @requires soovee.conf
        """
        from ..forms import Forms
        service = self._service
        cache = self._cache

        # Show directory dialog to choose enclosures' location.
        directory = wx.DirDialog (
            parent=self._parent,
            message="Store serial audio enclosures.",
            defaultPath=Account.get("xLastDir", HOMEDIR),
            style=wx.PD_APP_MODAL|wx.DD_DEFAULT_STYLE)
        if directory.ShowModal() == wx.ID_OK:
            Account['xLastDir'] = directory.GetPath()
            directory.Destroy()
        else: 
            directory.Destroy()
            return

        # Show progress dialog for episodes' retrievals
        progressDlg = wx.ProgressDialog ( 
            parent=self._parent,
            title="Downloading serial audio enclosures.",
            message="Please, wait while feed enclosures are downloaded.",
            maximum=len(self._encls[1]),
            style=wx.PD_APP_MODAL|wx.PD_AUTO_HIDE|wx.PD_CAN_ABORT)
        feedtitle = service.toRss(self._encls[0])[:-4]
        progressDlg.SetIcon(main.app_icon())
        
        # Retrieve each epsiode placing in chosen location
        hook = __reportHook(interface=progressDlg,service=service)
        try:
            for eps, url in ((service.LASTTWO.match(url), url) 
                for url in self._encls[1]
                ):
                hook.filename = "%s/%s" % (feedtitle, eps.group(2))
                cache.Cache(pathname=url, filename=hook.filename, data=False, 
                hook=hook.report, workstore=Account['xLastDir'])
                hook.count += 1
        
        except feed.UserCancel:
            progress.Destroy()
            return

        except cache.CacheException as errmsg:
            errorDlg (parent, 'Download Error', errmsg)
            progress.Destroy()
            return

        # Format an m3u playlist Forms
        composer = Forms.Get(command="m3u",formtype="enc")
        composer.write(filename="%s/%s.m3u" % (feedtitle, feedtitle), 
            workstore=Account['xLastDir'], data=self._encls[1])
        progress.Destroy()



class __reportHook(object):
    """
    Create a feedback method to monitor file download progress.

        - C{__reportHook(interface:obj, service:obj) -> None}
        - C{__reportHook.report(blockread:int, blocksize:int, filesize:int) 
            -> None}
    """
    count = 1
    filename = ""

    def __init__(self, obj, service):
        """
        @param obj: object interface that implements an Update method with
            boolean return to halt download progress.

        @type obj: object
        @param service: Initialized soovee.conf.serviceConf object.
        @type service: object
        @return:
        @rtype: None
        """
        self._interface = obj
        self.toMB = service.toMB
        self.toKB = service.toKB

    def report(self, blockread, blocksize, filesize):
        """
        Progress report hook to show file percentage recieved.
        
        @param blockread: interger
        @type blockread: blocks read so far
        @param blocksize: interger
        @type blocksize: size of block read
        @param filesize: interger
        @type filesize: total size of file
        @return:
        @rtype: None
        @raises feed.UserCancel: User chooses to cancel operation
        """
        totalsize  = float(blockread * blocksize)
        size = ("%.0f kb" % self.toKB(totalsize)
            if totalsize < float(1048576)
            else "%.1f mb" % self.toMB(totalsize))
        checkReturn = self._interface.Update(self.count, "Received %s of %s." % (
            size, self.filename))
        if not checkReturn[0]: raise feed.UserCancel("Download ended by user")
        
