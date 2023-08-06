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

    - C{Format.write(filename:str, workstore:str, data:list, cache=None:obj, 
        rx=None:obj) -> None}
    - C{Format.item(item:dict, feed={}:dict, rx=None:obj) -> None}
"""


class Format():
    """
    Create a html page with serial audio info sections. Shows opml title page, 
    description and cover.

        - C{Format.write(filename:str, workstore:str, data:list, cache=None:obj,
            rx=None:obj) -> None}
        - C{Format.item(item:dict, feed={}:dict, rx=None:obj) -> None}
    """

    method = ("htm","view") #: Tuple of type and format
    filename = "sv%s.html" #: Default file name for page

    def write(self, filename, workstore, data, cache=None, rx=None):
        """
        Initialize and write a html page with serial audio info sections. The 
        passed Opml data is used to build the sections.

        @param filename: Local path-filename fragment.
        @type filename: basestring
        @param workstore: Base path-filename to store filename under.
        @type workstore: basestring
        @param data: List of Opml feed data to help build a page.
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
        from ..lib.sv_file import setName
        workFile = setName(filename=filename, workstore=workstore)
        fileobj = open(workFile, "w")
        fileobj.write("<h1>SooVee Serial Audio feeds</h1>\n")
        for item in data:
            print "Creating section for %s." % item['title']
            fileobj.write(self.item(item).encode("ascii", "xmlcharrefreplace"))
        fileobj.close()

    def item(self, item, feed={}, rx=None):
        """
        Format an html section for a feed subscription using data found in its 
        Opml feed entry.

        @param item: Opml data
        @type item: dict
        @param feed: Rss data. Default dict.
        @type feed: dict
        @param rx: Unused for this format. Default None.
        @type rx: obj
        @return:
        @rtype: basestring
        @raise TypeError: item passed was not a dict
        """
        if not isinstance(item, dict): raise TypeError("requires type dict.")
        page=[]
        #
        # Compose common dictionary elements
        #
        page.append(
            ("<div id=\"book\">\n<h1 id=\"title\">%(title)s</h1><a href=\""
            "%(htmlUrl)s\"><img id=\"cover\" style=\"float: left; margin: "
            "6px 6px 6px 6px; \" src=\"%(imgUrl)s\"/></a>") % item
            )
        #
        # Compose an Rss-based dictionary
        #
        if item['type'].lower() == "rss":
            page.append(
                ("<p>Subcribed Id: %(subId)s<br/>\nCurrent Status: %(status)s"
                "</p>\n<ul id=\"links\">\n<li>%(xmlUrl)s</li>\n<li>%(altUrl)s"
                "</li>\n</ul>") % item
                )
        #
        # Compose an Htm-based dictionary
        #
        elif item['type'].lower() == "htm":
            page.append("<p>%(description)s</p>" % item)
        page.append("<br clear=\"all\"/></div>")
        return "\n".join(page)
