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
SooVee Serial Audio Manger - Html pages with index for the forms module plugin. 
It will create a page for each serial audio feed in ./books and a link to it on
the index page.in the parent folder. 

This plugin was developed specificaly for soovee.gui summary view. It lacks the 
cover image and sets a few class attributes as well.

    - C{Format.write(filename:str, workstore:str, data:list, cache=None:obj, 
        rx=None:obj) -> None}
    - C{Format.item(item:dict, feed=None:dict, rx=None:obj) -> None}

@requires: soovee.lib.sv_Data
"""
from ..lib.sv_data import Rss as rssFeed #: Rss data parsers
from ..conf import CACHEDIR

class Format():
    """
    Create a set of html pages in ./books with an index. Shows opml title, 
    page, and description as well as rss episode title, author, category, file 
    location and length in MB.

        - C{Format.write(filename:str, workstore:str, data:list, cache=None:obj,
            rx=None:obj) -> None}
        - C{Format.item(item:dict, feed={}:dict, rx=None:obj) -> None}
    """
    method = ("frm","view") #: Tuple of type and format
    filename = "index.html" #: Default file name for index

    def write(self, filename, workstore, data, cache=None, rx=None):
        """
        Initialize and write set of html pages in ./books with an index. The 
        passed Opml data is used to retrieve the data for each Rss feed.

        @param filename: Local path-filename fragment.
        @type filename: basestring
        @param workstore: Base path-filename to store filename under.
        @type workstore: basestring
        @param data: List of Opml feed data to help build pages and locate Rss 
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
        from ..lib.sv_file import setName, os
        workFile = setName(filename=filename, workstore=workstore)
        fileobj_index = open(workFile, "w")
        fileobj_index.write("<h1>Soovee Serial Audio feeds</h1>\n<ul>\n")
        for item in data:
            print "Creating page for %s." % item['title']
            #{ Read data for feed page
            rss = rssFeed(cache.Cache(item['xmlUrl'], rx.toRss(item['title']),
                workstore=CACHEDIR).data())
            #{ Write data for feed page
            fileobj_page = open(
                setName(filename=os.path.join("books", 
                "%s.html" % rx.toRss(item['title'])[:-4]), workstore=workstore), 
                "w")
            fileobj_page.write(
                self.item(item, rss, rx).encode("ascii", "xmlcharrefreplace")
                )
            fileobj_page.close()
            #{ Write data for feed page link to index page
            fileobj_index.write("<li><a href=\"%s\">%s</a><li>\n" % (
                filename, rx.PRETITLE.sub("", item['title'])))
        fileobj_index.write("</ul>\n")
        fileobj_index.close()

    def item(self, item, feed={}, rx=None ):
        """
        Format an html page for a feed subscription using data found in its Opml
        feed entry and in its Rss file. Store a filename for this page. Set 
        class attributes for use with soovee.gui summary view.

        @param item: Opml data
        @type item: dict
        @param feed: Rss data. Default dict.
        @type feed: dict
        @param rx: Intialized soovee.regex object. Default None.
        @type rx: obj
        @return:
        @rtype: basestring
        @raise TypeError: item or feed passed was not a dict
        """

        if not isinstance(item, dict) and not isinstance(feed, dict): 
            raise TypeError("requires type dict.")
        page = []

        #
        #{ Set page's filename
        #
        self.filename = "%(itunes:author)s-%(title)s.html"%(feed['sum'])
        feed['sum']['description'] = rx.PRESUMMARY.sub("", feed['sum']['description'])
        feed['sum']['category'] = feed['sum']['category'].split("; ")[2] #get 3rd
        #
        #{ Compose summary header data
        #
        page.append(
            ("<h1>%(title)s by %(itunes:author)s</h1><p><em>%(category)s</em>"
            "</p><p>%(description)s</p>") % feed['sum']
            )
        awards = rx.getImages(item['description'])
        if awards:
            page.append(
                "<p>%s</p>" % "".join(
                ["<img src=\"%s\" />"%(image) for image in awards]
                ))
        page.append("<hr />")
        #
        #{ Store values for use elsewhere
        #
        self.pageUrl = item['htmlUrl'] #: U{Podiobooks.com} audiobook web page
        self.imageUrl = feed['sum']['image']['url'] #: audiobook cover image
        self.feedTitle = feed['sum']['title'] #: audiobook title
        self.encloseUrls = [] #: audiobook's available episodes
        #
        #{ Format summary data fields from Rss Data <item>s
        #
        for episode in feed['eps']:
            episode['encllength'] = rx.toMB(episode['enclosure']['length'])
            episode['enclurl'] = episode['enclosure']['url']
            self.encloseUrls.append(episode['enclurl']) #: audiobook episode
            episode['description'] = rx.PREEPISODE.sub("", episode['description'])
            page.append(
                ("<dt><a href=\"%(enclurl)s\">%(title)s</a>(%(encllength).2f MB"
                ")</dt><dd>%(description)s</dd>") % episode
                )
        return "".join(page)
