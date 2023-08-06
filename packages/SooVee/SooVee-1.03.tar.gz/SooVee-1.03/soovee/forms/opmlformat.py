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
SooVee Serial Audio Manger - Opml file of serial audio info for the forms module
plugin. It will create a page containing a section for set of serial audio info.

This plugin was developed specificaly for soovee.pages data. 

    - C{Format.write(filename:str, workstore:str, data:list, cache=None:obj, 
        rx=None:obj) -> None}
    - C{Format.item(item:dict, feed={}:dict, rx=None:obj) -> None}
"""


class Format():
    """
    Create a Opml file with serial audio info sections. Shows Opml page, type,
    htmlUrl, xmlUrl, description, and text. Optional shows Opml imgUrl, altUrl,
    subId, and status. Value of Opml text defaults to title if absent.

        - C{Format.write(filename:str, workstore:str, data:list, cache=None:obj, 
            rx=None:obj) -> None}
        - C{Format.item(item:dict, feed={}:dict, rx=None:obj) -> None}
    """
    method = ("htm","opml") #: Tuple of type and format
    filename = "sv%s.opml" #: Default file name for page

    def write(self, filename, workstore, data, cache=None, rx=None):
        """
        Initialize and write an Opml file with serial audio info sections. The 
        passed Opml data is used to build the sections.

        @param filename: Local path-filename fragment.
        @type filename: basestring
        @param workstore: Base path-filename to store filename under.
        @type workstore: basestring
        @param data: List of Opml feed data to help build file.
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
        from soovee.lib.sv_file import setName
        workFile = setName(filename=filename, workstore=workstore)
        fileobj = open(workFile, "w")
        fileobj.write("<?xml version=\"1.0\" encoding=\"ISO-8859-1\"?>\n"
            "<opml version=\"1.1\">\n<head><title>SooVee Serial Audio Feeds"
            "</title>\n</head>\n<body>")
        for item in data: 
            print "Creating section for %s." % item['title']
            fileobj.write(self.item(item).encode("ascii", "xmlcharrefreplace"))
        fileobj.write("</body>\n</opml>")
        fileobj.close()

    def item(self, item, feed={}, rx=None):
        """
        Format an opml section for a feed subscription using data found in its 
        Opml feed entry.

        @param item: Opml data
        @type item: dict
        @param feed: Unused for this format. Default dict.
        @type feed: dict
        @param rx: Unused for this format. Default None.
        @type rx: obj
        @return:
        @rtype: basestring
        @raise TypeError: data passed was not a dict
        """
        if not isinstance(item, dict): raise TypeError("requires type dict.")
        opmlitem = []
        #
        # Set dictionary defaults
        #
        values = {
            'htmlUrl':item.get("htmlUrl",""),
            'title':item.get("title",""),
            'type':item.get("type",""),
            'xmlUrl':item.get('xmlUrl',""),
            'description':item.get('description',""),
            'text':item.get('text', item['title'])
            }
        #
        # Compose common dictionary elements
        #
        opmlitem.append(
            ("<outline title=\"%(title)s\" text=\"%(text)s\" type=\"%(type)s\" "
            "xmlUrl=\"%(xmlUrl)s\" htmlUrl=\"%(htmlUrl)s\"") % values
            )
        #
        # Compose possible dictionary elements
        #
        if item.has_key("imgUrl"):
            opmlitem.append(" imgurl=\"%s\"" % item['imgUrl'])
        if item.has_key("altUrl"):
            opmlitem.append(" alturl=\"%s\"" % item['altUrl'])
        if item.has_key("subId"):
            opmlitem.append(" subId=\"%s\"" % item['subId'])
        if item.has_key("status"):
            opmlitem.append(" status=\"%s\"" % item['status'])
        opmlitem.append("/>\n")
        return "".join(opmlitem)
