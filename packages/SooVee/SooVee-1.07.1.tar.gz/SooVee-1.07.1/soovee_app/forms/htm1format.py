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

    - C{write(filepath:str, workpath:str, data:list, cache:obj=None, 
        service:obj=None) -> None}
    - C{item(data:dict, feed:str=None, service:obj=None) -> str}
@requires: L{soovee_lib.parse}
"""
METHOD = ("frm","html") #: Tuple of type and format
FILENAME = "index.html" #: Default file name for index


def write(filepath, workpath, data, cache=None, service=None):
    """
    Initialize and write set of html pages in ./books with an index. The 
    passed Opml data is used to retrieve the data for each Rss feed.

    @param filepath: Local path-filename fragment.
    @type filepath: basestring
    @param workpath: Base path-filename to store filename under.
    @type workpath: basestring
    @param data: List of Opml feed data to help build pages and locate Rss 
        feed data.
    @type data: list
    @param cache: Intialized soovee.lib.sv_read object. Default None.
    @type cache: obj
    @param service: Intialized soovee.regex object. Default None.
    @type service: obj
    @return:
    @rtype: None
    @requires: L{soovee_lib.parse}
    @raise TypeError: data passed was not a list
    """
    if not isinstance(data, list): 
        raise TypeError("FormsWrite missing list.")

    from soovee_lib.parse import Xml #: Rss data parsers

    fileobj_index = open(cache.mkpath(filepath=filename, workpath=workstore),
        "w")
    fileobj_index.write("<h1>SooVee Serial Audio feeds</h1>\n<ul>\n")

    for opml in data:
        yield opml['title']

        #{ Read data for feed page
        rss = Xml.rss(cache.Cache(opml['xmlUrl']).data())

        #{ Write data for feed page
        filename = cache.mkpath(filepath=service.TOHTM(opml['title']), 
            workpath=workstore, subpath="books")
        fileobj_page = open(filename, "w")
        fileobj_page.write(
            item(opml, rss, service).encode("ascii", "xmlcharrefreplace")
            )
        fileobj_page.close()
        
        #{ Write data for feed page link to index page
        fileobj_index.write("<li><a href=\"%s\">%s</a><li>\n" % (
            filename, service.PRETITLE.sub("", opml['title'])))
        fileobj_page.close()
    
    fileobj_index.write("</ul>\n")
    fileobj_index.close()


def item(data, feed=None, service=None):
    """
    Format an html page for a feed subscription using data found in its Opml
    feed entry and in its Rss file. Store a filename for this page.

    @param data: Opml data.
    @type data: dict
    @param feed: Rss data. Default dict.
    @type feed: dict
    @param rx: Intialized soovee.regex object. Default None.
    @type rx: obj
    @return:
    @rtype: basestring
    @raise TypeError: item or feed passed was not a dict
    """
    if not isinstance(data, dict) and not isinstance(feed, dict): 
        raise TypeError("FormsItem missing dictionaries.")
    
    page = []

    feed['sum']['category'] = feed['sum']['category'].split("; ")[2] #:get 3rd
    feed['sum']['imageurl'] = feed['sum']['image']['url']
    awards = service.GETIMAGES(data['description'])
    if awards:
        feed['sum']['award'] = "".join(
            [("<img id=\"award\" src=\"%s\" />" % image) for image in awards]
            )
    
    else: 
        feed['sum']['award'] = ""

    #{ Compose summary header data
    page.append(
        ("<div id=\"header\">\n<h1 id=\"title\">%(title)s by "
        "%(itunes:author)s</h1>\n<p id=\"type\">%(category)s</p>\n</div>"
        "\n<div id=\"synopsis\">\n<img id=\"cover\" style=\"float: left; "
        "margin: 6px 6px 6px 6px; width: 145px; \" src=\"%(imageurl)s\"/>"
        "\n<p>%(description)s</p>\n</div>\n%(award)s<hr /><br clear=\"all"
        "\" />") % feed['sum']
        )

    #{ Compose each episode's data
    for episode in feed['eps']:
        episode['encllength'] = service.TOMB(episode['enclosure']['length'])
        episode['enclurl'] = episode['enclosure']['url']
        episode['description'] = service.PREEPISODE.sub(
            "", episode['description'])
        page.append(
            ("<div id=\"episodes\">\n<dt class=\"episode\"><a href=\""
            "%(enclurl)s\">%(title)s</a> <span style=\"font-size: 8pt; \">"
            "(%(encllength).2f MB)</span></dt>\n<dd>%(description)s"
            "</dd>") % episode
            )
    return "\n".join(page)
