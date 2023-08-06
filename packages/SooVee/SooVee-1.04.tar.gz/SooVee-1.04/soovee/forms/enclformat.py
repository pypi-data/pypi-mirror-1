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
SooVee Serial Audio Manger - Mp3 Playlist for the forms module plugin. It will
create a valid m3u formated file.

    - C{Format.write(filename:str, workstore:str, data:list, cache=None:obj, 
        rx=None:obj) -> None}
    - C{Format.item(item:dict, feed={}:dict, rx=None:obj) -> None}
"""


class Format():
    """
    Create a valid m3u file. Write the data list pased which should be mp3 
    enclosures to filename in workstore.

        - C{Format.write(filename:str, workstore:str, data:list, cache=None:obj, 
            rx=None:obj) -> None}
        - C{Format.item(item:dict) -> None}
    """
    method = ("enc","m3u") #: Tuple of type and format

    def write(self, filename, workstore, data, cache=None, rx=None):
        """
        Initialize and write m3u file header.

        @param filename: Local path-filename fragment.
        @type filename: basestring
        @param workstore: Base path-filename to store filename under.
        @type workstore: basestring
        @param data: List of mp3 enclosures to put in filename.
        @type data: list
        @param cache: Unused for this format. Default None.
        @type cache: obj
        @param rx: Unused for this format. Default None.
        @type rx: obj
        @return:
        @rtype: None
        @requires: L{soovee.lib.sv_file}
        @raise TypeError: data passed was not a list
        """
        if not isinstance(data, list): raise TypeError("requires type list.")
        from ..lib.sv_file import setName, os
        workFile = setName(filename=filename, workstore=workstore)
        workPath = os.path.split(workFile)
        fileobj = open(workFile, "w")
        fileobj.write("#EXTM3U\r\n")
        filelist = os.listdir(workPath[0])
        filelist.sort() #: Must sort to have serial audio in order in file
        for item in filelist:
            if item.endswith('.mp3'):
                fileobj.write(self.item(os.path.join(workPath[0], item)))
        fileobj.close()

    def item(self, item, feed={}, rx=None):
        """
        Read mp3 file's tag info to get title and length to add #EXTINF to
        path-filename information.

        @param item: mp3 filename
        @type item: basestring
        @param feed: Unused for this format. Default dict.
        @type feed: basestring
        @param rx: Unused for this format. Default None.
        @type rx: obj
        @return:
        @rtype: basestring
        @requires: eyeD3.tag
        @raise TypeError: item passed was not a basestring.
        """
        if not isinstance(item, basestring): 
            raise TypeError("requires type basestring.")
        import eyeD3.tag as tags
        if tags.isMp3File(item):
            try:
                tagsobj = tags.Mp3AudioFile(item)
            except tags.TagException:
                return item

            return "#EXTINF:%s, %s\r\n%s\r\n" % (tagsobj.play_time,
                (tagsobj.getTag().getTitle() or item[:-4]), item)
