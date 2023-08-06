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

    - C{METHOD:tuple}
    - C{write(filepath:str, workpath:str, data:list, cache:obj=None, 
        service:obj=None) -> None}
    - C{item(data:dict, feed:dict=None, service:obj=None) -> str}
"""
METHOD = ("enc","m3u") #: Tuple of type and format

def write(filepath, workpath, data, cache=None, service=None):
    """
    Initialize and write m3u file header.

    @param filepath: Local path-filename fragment.
    @type filepath: basestring
    @param workpath: Base path-filename to store filename under.
    @type workpath: basestring
    @param data: List of mp3 enclosures to put in filename.
    @type data: list
    @param cache: Unused for this format. Default None.
    @type cache: obj
    @param service: Unused for this format. Default None.
    @type service: obj
    @return:
    @rtype: None
    @raise TypeError: data passed was not a list
    """
    if not isinstance(data, list): 
        raise TypeError("FormsWrite missing list.")
    filepath = cache.mkpath(filepath=filepath, workpath=workpath)
    workpath = cache.os.path.split(filepath)[0]
    fileobj = open(filepath, "w")
    fileobj.write("#EXTM3U\r\n")
    for url in data:
        encl = service.LASTTWO.match(url).group(2)
        yield encl
        if encl.endswith('.mp3'):
            fileobj.write(item(cache.mkpath(filepath=encl, workpath=workpath)))
    fileobj.close()

def item(data, feed=None, service=None):
    """
    Read mp3 file's tag info to get title and length to add #EXTINF to
    path-filename information.

    @param data: mp3 filename
    @type data: basestring
    @param feed: Unused for this format. Default dict.
    @type feed: basestring
    @param service: Unused for this format. Default None.
    @type service: obj
    @return:
    @rtype: basestring
    @requires: eyeD3.tag
    @raise TypeError: data passed was not a basestring.
    """
    if not isinstance(data, basestring): 
        raise TypeError("FormsItem missing basestring.")

    import eyeD3.tag as tags

    if tags.isMp3File(data):
        try: tagsobj = tags.Mp3AudioFile(data)

        except tags.TagException:
            return data

        return "#EXTINF:%s, %s\r\n%s\r\n" % (tagsobj.play_time,
            (tagsobj.getTag().getTitle() or data[:-4]), data)
