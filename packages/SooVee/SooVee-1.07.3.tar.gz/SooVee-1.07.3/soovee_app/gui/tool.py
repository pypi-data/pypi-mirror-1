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

@requires: wx
@requires: wx.lib.pubsub
@requires: {soovee_app.gui.main}
@requires: {soovee_app.gui.feed}
@requires: {soovee_lib.parse}
@requires: {soovee_app.conf}
@requires: {soovee_lib.report}
@requires: {soovee_app.forms}
"""
import wx , wx.lib.pubsub as msg
import feed, main


TRANSCIEVER = msg.Publisher() #: Interobject communication object.


class Update(object):
    """
    """
    def __init__(self, parent, cache, service, opml):
        """
        Initialize a download of serial audio feed enclosures. 
        
        @param parent: parent wx object.
        @type parent: object
        @param cache: Initialized soovee_lib.cache object.
        @type cache: object
        @param service: Initialized soovee_app.conf.serviceConf object.
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

    def feeds(self, message=None):
        """
        Update account subscribed serial audio feeds.

        @response: C{_UPDATE}
        @announce: C{FEED_RFRESH} -- 
                I{New Opml list data for consumption}

        @return: 
        @rtype: None
        @requires: L{soovee_lib.ckuri}
        """
        from soovee_lib.ckuri import Refresh
        try:
            # Update serial audio feed list by passing opmlpath to feed
            opmldata = Refresh(cache=self._cache, path=self._opml)

            # Show wx.ProgressDialog to track update progress
            progressdlg = wx.ProgressDialog (
                parent=self._parent, title="Updating serial audio content.",
                message="Please, wait while cached feeds are updated.",
                maximum=len(opmldata),
                style=wx.PD_APP_MODAL|wx.PD_AUTO_HIDE|wx.PD_CAN_ABORT)
            progressdlg.SetIcon(main.app_icon())

            # Update Rss data by iterating new feed list
            for index, title in opmldata:
                checkreturn = progressdlg.Update(index, 
                    self._service.PRETITLE.sub("", title))
                if not checkreturn[0]: 
                    break #: Monitor for user cancel

        except self._cache.CacheException as errmsg:
            feed.errordlg (parent=self._parent, title='Caching Error',
                message=errmsg)

        TRANSCIEVER.sendMessage(topic="FEED_RFRESH", data=opmldata.opml)
        progressdlg.Destroy()
        



class Download(object):
    """
    Download serial audio feed enclosures from a service account. Monitor
    TRANSCIEVER for 'FEED_DATA' to collect feed title and enclosures.
        
        - C{Download(parent:obj, cache:obj, service:obj) -> None}
        - C{Download.getEncls(None) -> None}
        
    @response: C{FEED_DATA}
    """
    _encls = []

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
        TRANSCIEVER.subscribe(topic="FEED_DATA", listener=self._setencls)

    def _setencls(self, message):
        """
        Collect serial audio feed.data to enable retrieval of episodes.

        @response: C{FEED_DATA} --
            I{Dictionary of useful Rss Data.}
        @param message: TRANSCIEVER object
        @type message: object
        @return:
        @rtype: None
        """
        data = message.data
        if isinstance(data, dict):
            self._encls = (data['feedtitle'], data['encloseurl'])

    def encls(self, message=None):
        """
        Download serial audio feed enclosures from a service account to user
        chosen location with visual feedback of progess

        @return:
        @rtype: None
        @requires L{soovee_app.forms}
        @requires L{soovee_app.conf}
        @requires L{soovee_lib.report}
        """
        
        from ..conf import ACCOUNT
        service = self._service
        cache = self._cache

        # Show directory dialog to choose enclosures' location.
        directory = wx.DirDialog (
            parent=self._parent,
            message="Store serial audio enclosures.",
            defaultPath=ACCOUNT.get("xLastDir", cache.HOMEPATH),
            style=wx.PD_APP_MODAL|wx.DD_DEFAULT_STYLE)
        if directory.ShowModal() == wx.ID_OK:
            ACCOUNT['xLastDir'] = directory.GetPath()
            directory.Destroy()
        else: 
            directory.Destroy()
            return

        # Show progress dialog for episodes' retrievals
        progressdlg = wx.ProgressDialog ( 
            parent=self._parent,
            title="Downloading serial audio enclosures.",
            message="Please, wait while feed enclosures are downloaded.",
            maximum=len(self._encls[1]),
            style=wx.PD_APP_MODAL|wx.PD_AUTO_HIDE|wx.PD_CAN_ABORT)
        feedtitle = service.TORSS(self._encls[0])[:-4]
        progressdlg.SetIcon(main.app_icon())
        # Retrieve each epsiode placing in chosen location
        from soovee_lib.report import Hook
        hook = Hook(interface=progressdlg, service=service)
        try:
            for url in self._encls[1]:
                eps = service.LASTTWO.match(url)
                hook.filename = "%s/%s" % (feedtitle, eps.group(2))
                cache.Cache(urlpath=url, filepath=hook.filename, 
                    hook=hook.report, workpath=ACCOUNT['xLastDir'])
                hook.count += 1
        
        except feed.UserCancel:
            progressdlg.Destroy()
            return

        except cache.CacheException as errmsg:
            feed.errordlg (self._parent, 'Download Error', errmsg)
            progressdlg.Destroy()
            return

        # Format an m3u playlist Forms
        from ..forms import FORMS as Forms
        composer = Forms.get(command="m3u", form="enc")
        for mp3file in composer.write(filepath="%s/%s.m3u" % (feedtitle,
            feedtitle), workpath=ACCOUNT['xLastDir'], data=self._encls[1], 
            cache=cache, service=service):
            checkreturn = progressdlg.Update(hook.count, 
                "Writing M3U Playlist")
            if not checkreturn[0]: 
                raise feed.UserCancel("Download ended by user")
        progressdlg.Destroy()

