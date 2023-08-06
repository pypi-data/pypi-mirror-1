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
SooVee Serial Audio Manger - Html page of serial audio info for the forms module
plugin. It will create a page containing a section for set of serial audio info.

This plugin was developed specificaly for soovee.pages data. 

    - C{write(filepath:str, workpath:str, data:list, cache:obj=None, 
        service:obj=None) -> None}
    - C{item(item:dict, feed:dict=None, service:obj=None) -> str}
"""

METHOD = ("htm","view") #: Tuple of type and format
FILENAME = "sv%s.html" #: Default file name for page

def write(filepath, workpath, data, cache=None, service=None):
    """
    Initialize and write a html page with serial audio info sections. The 
    passed Opml data is used to build the sections.

    @param filepath: Local path-filename fragment.
    @type filepath: basestring
    @param workpath: Base path-filename to store filename under.
    @type workpath: basestring
    @param data: List of Opml feed data to help build a page.
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

    fileobj = open(cache.mkpath(filepath=filepath, workpath=workpath), "w")
    fileobj.write("<h1>SooVee Serial Audio feeds</h1>\n")

    for opml in data:
        yield opml['title'] #MAYBE YIELD?
        fileobj.write(item(opml).encode("ascii", "xmlcharrefreplace"))

    fileobj.close()

def item(data, feed=None, service=None):
    """
    Format an html section for a feed subscription using data found in its 
    Opml feed entry.

    @param data: Opml data
    @type data: dict
    @param feed: Rss data. Default dict.
    @type feed: dict
    @param service: Unused for this format. Default None.
    @type service: obj
    @return:
    @rtype: basestring
    @raise TypeError: item passed was not a dict
    """
    if not isinstance(data, dict): 
        raise TypeError("FormsItem missing dictionaries.")

    page = []

    # Compose common dictionary elements
    page.append(
        ("<div id=\"book\">\n<h1 id=\"title\">%(title)s</h1><a href=\""
        "%(htmlUrl)s\"><img id=\"cover\" style=\"float: left; margin: "
        "6px 6px 6px 6px; \" src=\"%(imgUrl)s\"/></a>") % data
        )

    # Compose with rss-based data
    if data['type'].lower() == "rss":
        page.append(
            ("<p>Subcribed Id: %(subId)s<br/>\nCurrent Status: %(status)s"
            "</p>\n<ul id=\"links\">\n<li>%(xmlUrl)s</li>\n<li>%(altUrl)s"
            "</li>\n</ul>") % data
            )

    # Compose with htm-based data
    elif data['type'].lower() == "htm":
        page.append("<p>%(description)s</p>" % data)
    page.append("<br clear=\"all\"/></div>")

    return "\n".join(page)
