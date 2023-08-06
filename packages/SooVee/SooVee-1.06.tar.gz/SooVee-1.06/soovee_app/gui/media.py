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
SooVee Serial Audio Manger - Media support module for the graphical inface. It
handles the listening of audio enclosures found in a serial audio feed.

    - C{MediaCptn(parent:object) -> None}
    - C{MediaCptn(parent:object) -> None}
    - C{PositionCtrl(parent:object) -> None}
    - C{ListenCtrl(parent:object) -> None}

@newfield announce: Announce with TRANSCIEVER
@newfield response: Response for TRANSCIEVER
@newfield handle: Handle wx.Event

@requires: wx
@requires: wx.lib.pubsub

"""

import wx
import wx.lib.pubsub as msg
from soovee_lib.enclist import Que as MediaPlaylist

TRANSCIEVER = msg.Publisher() #: Interobject communication object.
MEDIAPLAYER = None #: wx.Media Object passed by soovee.gui.main

#
#{ Media Controls
#
class MediaCptn(wx.StaticText):
    """
    Display mediaplayer caption.

        - C{MediaCptn(parent:object) -> None}

    @response: C{MEDIA_CHOICE}
    @response: C{FEED_CHOICE}
    """

    def __init__(self, parent):
        """
        Create a wx.StaticText to hold current set file for MEDIAPLAYER.

        @param parent: parent wx.Window object
        @type parent: object
        @return:
        @rtype: None
        """

        wx.StaticText.__init__(self, parent, wx.ID_ANY,
            label="Select Serial Audio Episode to play", size=(200, -1))
        TRANSCIEVER.subscribe(listener=self.__updateenclosure,
            topic="MEDIA_CHOICE")
        TRANSCIEVER.subscribe(listener=self.__revertenclosure,
            topic="FEED_CHOICE")

    def __updateenclosure(self, message):
        """
        Extract and set media file name from web url.

        @response: C{MEDIA_CHOICE} --
            I{Url string of clicked audio file link}
        @param message: TRANSCIEVER object
        @type message: object
        @return:
        @rtype: None
        """
        if not isinstance(message.data, basestring): 
            raise TypeError
        self.SetLabel(message.data.rsplit("/", 1)[1])

    def __revertenclosure(self, message):
        """
        Reset caption to default.

        @response: C{FEED_CHOICE} --
            I{Index interger of L{Data.PbOpml} query}
        @param message: TRANSCIEVER object
        @type message: object
        @return:
        @rtype: None
        """
        self.SetLabel("Select a Serial Audio Episode")


class PositionCtrl(wx.Slider):
    """
    MEDIAPLAYER control to set a position in an episode of a Podiobooks.com
    audio book. Uses wx.Timer to update wx.Slider of MEDIAPLAYER's current file 
    position.

        - C{PositionCtrl(parent:object) -> None}

    @response: C{MEDIA_CHOICE}
    @response: C{FEED_CHOICE}
    """
    __tvalue = 0
    _playlist = []

    def __init__(self, parent):
        """
        Create a wx.Slider positional control for MEDIAPLAYER.

        @param parent: parent wx.Window object
        @type parent: object
        @return:
        @rtype: None
        """
        wx.Slider.__init__(self, parent, wx.ID_ANY, value=0, minValue=0,
            maxValue=1, size=(200, -1), style=wx.SL_AUTOTICKS)
        self.Bind(event=wx.EVT_SLIDER, handler=self.__positionenclosure)
        self.Enable(False)
        #=== Set timer to monitor MEDIAPLAYER
        self.timer = wx.Timer(owner=self, id=wx.ID_ANY)
        self.Bind(event=wx.EVT_TIMER, handler=self.__monitorenclosure)
        self.Bind(event=wx.EVT_TIMER, handler=self.__monitorenclosure)
        #=== Monitor MEDIAPLAYER for media finish to advance to next episode.
        MEDIAPLAYER.Bind(event=wx.media.EVT_MEDIA_FINISHED, 
            handler=self.__doneenclosure)
        TRANSCIEVER.subscribe(listener=self.__startenclosure,
            topic="MEDIA_CHOICE")
        TRANSCIEVER.subscribe(listener=self.__stopenclosure,
            topic="FEED_DATA")

    def __startenclosure(self, message):
        """
        Enable control and begin monitoring MEDIAPLAYER.

        @response: C{MEDIA_CHOICE} --
            I{Url string of clicked audio file link}
        @param message: TRANSCIEVER object
        @type message: object
        @return:
        @rtype: None
        """
        self._playlist.set(message.data)
        self.Enable(True)
        self.timer.Start(milliseconds=100) # update every 100 milliseconds

    def __stopenclosure(self, message):
        """
        Disable control and stop monitoring L{MEDIAPLAYER}.

        @response: C{FEED_CHOICE} --
            I{Index interger of L{Data.PbOpml} query}
        @param message: TRANSCIEVER object
        @type message: object
        @return:
        @rtype: None
        """
        self.Enable(False)
        self.timer.Stop()
        self._playlist = MediaPlaylist(enclosures=message.data['encloseurl'])
        self._playlist.next()

    def __positionenclosure(self, event):
        """
        Set arbitrary position for MEDIAPLAYER current file with wx.Slider

        @handle: C{wx.EVT_SLIDER} on self
        @param event: wx.Event object
        @type event: object
        @return:
        @rtype: None
        """
        MEDIAPLAYER.Seek(self.GetValue())

    def __doneenclosure(self, event):
        """
        Set MEDIAPLAYER to next episode in playlist and fire new 'MEDIA_CHOICE'.
        
        @handle: C{wx.media.EVT_MEDIA_FINISHED} on MEDIAPLAYER
        @param event: wx.media.EVT_MEDIA_FINISHED object
        @type event: object
        @return:
        @rtype: None
        """
        try:
            TRANSCIEVER.sendMessage(topic="MEDIA_CHOICE",
                data=self._playlist.next())
        except StopIteration:
            MEDIAPLAYER.Stop()

    def __monitorenclosure(self, event):
        """
        Adjust wx.Slider to MEDIAPLAYER current file length and position.

        @handle: C{wx.EVT_TIMER} on self
        @param event: C{wx.Event} object
        @type event: object
        @return:
        @rtype: None
        """

        if MEDIAPLAYER and not (MEDIAPLAYER.GetDownloadProgress() < 1 and
            MEDIAPLAYER.GetDownloadTotal() < 1):
            self.SetRange(0, MEDIAPLAYER.Length())
            self.SetValue(MEDIAPLAYER.Tell())


class ListenCtrl(wx.Button):
    """
    MEDIAPLAYER control to set its current state to either play() or 
    pause().

        - C{ListenCtrl(parent:object) -> None}

    @response: C{FEED_DATA}
    @response: C{MEDIA_CHOICE}
    """

    def __init__(self, parent):
        """
        Create Play/Pause wx.Button for MEDIAPLAYER.

        @param parent: parent wx.Window object
        @type parent: object
        @return:
        @rtype: None
        """
        wx.Button.__init__(self, parent, wx.ID_ANY, label="Play Episode",
                    size=(200, -1))
        self.Bind(event=wx.EVT_BUTTON, handler=self.__listenenclosure)
        self.Enable(False)
        TRANSCIEVER.subscribe(listener=self.__intializeenclosure,
            topic="MEDIA_CHOICE")
        TRANSCIEVER.subscribe(listener=self.__changeenclosure,
            topic="FEED_CHOICE")

    def __changeenclosure(self, message):
        """
        Disable wx.Button as a new serial audio feed has been selected.

        @response: C{FEED_DATA} --
            I{Dictionary of useful Rss Data.}
        @param message: TRANSCIEVER object
        @type message: object
        @return:
        @rtype: None
        """
        if MEDIAPLAYER:
            MEDIAPLAYER.Stop()
            self.Enable(False)

    def __intializeenclosure(self, message):
        """
        Initialize MEDIAPLAYER with chosen selection. Enable control as
        MEDIAPLAYER has an actual file to hear episode.

        @response: C{MEDIA_CHOICE} --
            I{Dictionary of useful Rss Data.}
        @param message: TRANSCIEVER object
        @type message: object
        @return:
        @rtype: None
        """
        if MEDIAPLAYER and MEDIAPLAYER.LoadURI(message.data):
            self.Enable(True)
            self.__listenenclosure(message, True)

    def __listenenclosure(self, message, load=False):
        """
        Set MEDIAPLAYER object state to play() or pause().

        @handle: C{wx.EVT_BUTTON} on self
        @param message: Either wx.Event or TRANSCIEVER object
        @type message: object
        @param load: Is this a new file to play.
        @type load: bool
        @return:
        @rtype: None
        """
        state = (1 if load else MEDIAPLAYER.GetState() if MEDIAPLAYER else None)

        if state == 1: # Current state is pause. Call MEDIAPLAYER.Play().
            MEDIAPLAYER.Play()
            self.SetLabel("Pause Episode")
            #self.SetToolTip(wx.ToolTip("press to pause"))

        elif state == 2: # Current state is play. Call MEDIAPLAYER.Pause().
            MEDIAPLAYER.Pause()
            self.SetLabel("Play Episode")
            #self.SetToolTip(wx.ToolTip("press to play"))
