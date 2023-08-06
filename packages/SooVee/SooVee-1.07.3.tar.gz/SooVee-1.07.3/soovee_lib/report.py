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
SooVee Serial Audio Manager - Cache progress hook library.

    - C{Hook(interface:obj, service:obj) -> None}
    - C{Hook.report(blockread:int, blocksize:int, filesize:int) -> None}
"""

class Hook(object):
    """
    Create a feedback method to monitor file download progress.

        - C{Hook(obj:obj, service:obj) -> None}
        - C{Hook.report(blockread:int, blocksize:int, filesize:int) -> None}

    """
    count = 1
    filename = ""

    def __init__(self, interface, service):
        """
        Initialize a report hook with interface and service objects.

        @param interface: object interface that implements an Update method with
            boolean return to halt download progress.
        @type interface: object
        @param service: Initialized soovee.conf.serviceConf object.
        @type service: object
        @return:
        @rtype: None
        """
        self._interface = interface
        self.tomb = service.TOMB
        self.tokb = service.TOKB

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
        currentsize  = float(blockread * blocksize)
        currentsize = ("%.0f kb" % self.tokb(currentsize)
            if currentsize < float(1048576)
            else "%.1f mb" % self.tomb(currentsize))
        totalsize = ("%.0f kb" % self.tokb(filesize)
            if filesize < float(1048576)
            else "%.1f mb" % self.tomb(filesize))
        checkreturn = self._interface.Update(self.count, 
            "Received %s/%s of %s." % (currentsize, totalsize, 
            self.filename))
        if not checkreturn[0]: 
            raise feed.UserCancel("Download ended by user")

