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
SooVee Serial Audio Manger - Text page of serial audio feeds for the forms 
module plugin. It will create a summary page containing a section for set of 
serial audio feeds.

    - C{Format.write(filename:str, workstore:str, data:list, cache=None:obj, 
        rx=None:obj) -> None}
    - C{Format.item(item:dict, feed={}:dict, rx=None:obj) -> None}

@requires: soovee.lib.sv_Data
"""
from ..lib.sv_data import Rss as rssFeed #: Rss data parsers
from ..lib.sv_wrap import wrapText #: Line wrapper

class Format():
    """
    Create a text page. Shows Opml title, page, and description, as
    well as Rss episode title and length in MB.

        - C{Format.write(filename:str, workstore:str, data:list, cache=None:obj,
            rx=None:obj) -> None}
        - C{Format.item(item:dict, feed={}:dict, rx=None:obj) -> None}
    """
    method = ("frm","sumtxt") #: Tuple of type and format
    filename = "svsum.txt" #: Default file name for page

    def write(self, filename, workstore, data, cache=None, rx=None):
        """
        Initialize and write a summary text page. The passed Opml data is used 
        to retrieve the data for each Rss feed.

        @param filename: Local path-filename fragment.
        @type filename: basestring
        @param workstore: Base path-filename to store filename under.
        @type workstore: basestring
        @param data: List of Opml feed data to help build a page and locate Rss 
            feed data.
        @type data: list
        @param cache: Intialized soovee.lib.sv_read object. Default None.
        @type cache: obj
        @param rx: Intialized soovee.regex object. Default None.
        @type rx: obj
        @return:
        @rtype: None
        @requires: L{soovee.lib.sv_file}
        @raise TypeError: data passed was not a list
        """
        if not isinstance(data, list): raise TypeError("requires type list.")
        from ..lib.sv_file import setName
        workFile = setName(filename=filename, workstore=workstore)
        fileobj = open(workFile, "w")
        for item in data:
            print "Creating section for %s." % item['title']
            #
            #{ Get rss feed based on its title
            #
            rss = rssFeed(cache.Cache(item['xmlUrl'], rx.toRss(item['title']),
                workstore=workstore).data())
            fileobj.write(
                self.item(item, rss, rx).encode("ascii", "xmlcharrefreplace")
                )
        fileobj.close()

    def item(self, item, feed={}, rx=None):
        """
        Format an text section page for a feed subscription using data found in 
        its Opml feed entry and in its Rss file.

        @param item: Opml data
        @type item: dict
        @param feed: Rss data. Default dict.
        @type feed: dict
        @param rx: Intialized soovee.regex object. Default None.
        @type rx: obj
        @return:
        @rtype: basestring
        @raise TypeError: data or feed passed was not a dict
        """
        if not isinstance(item, dict) and not isinstance(feed, dict): 
            raise TypeError("requires type dict.")
        #
        #{ Compose summary header data
        #
        page = ["=" * 80,
            "\n".join(
                wrapText("FEED TITLE: %s" % PRETITLE.sub("", item['title']))
                ),
            "\n".join(
                wrapText("FEED PAGE: %s " % item['htmlUrl'])
                )
            ]
        #
        #{ Compose each episode's data
        #
        for episode in feed['eps']:
            audiofile = "%s (%.2f MB)" % (episode['title'],
                toMB(episode['enclosure']['length']))
            subpage = [
                "\n".join(
                    wrapText("EPISODE AUDIOFILE: %s" % audiofile, 4)
                    )
                ]
            page.append("\n".join(subpage))
        return "\n".join(page)

