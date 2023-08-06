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

    - C{write(filepath:str, workpath:str, data:list, cache:obj=None, 
        service:obj=None) -> None}
    - C{item(data:dict, feed:dict=None, service:obj=None) -> None}
"""

METHOD = ("htm","opml") #: Tuple of type and format
FILENAME = "sv%s.opml" #: Default file name for page

def write(filepath, workpath, data, cache=None, service=None):
    """
    Initialize and write an Opml file with serial audio info sections. The 
    passed Opml data is used to build the sections.

    @param filepath: Local path-filename fragment.
    @type filepath: basestring
    @param workpath: Base path-filename to store filename under.
    @type workpath: basestring
    @param data: List of Opml feed data to help build file.
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
    fileobj.write("<?xml version=\"1.0\" encoding=\"ISO-8859-1\"?>\n"
        "<opml version=\"1.1\">\n<head><title>SooVee Serial Audio Feeds"
        "</title>\n</head>\n<body>")

    for opml in data: 
        yield opml['title']
        fileobj.write(item(opml).encode("ascii", "xmlcharrefreplace"))

    fileobj.write("</body>\n</opml>")
    fileobj.close()

def item(data, feed=None, service=None):
    """
    Format an opml section for a feed subscription using data found in its 
    Opml feed entry.

    @param data: Opml data
    @type data: dict
    @param feed: Unused for this format. Default dict.
    @type feed: dict
    @param service: Unused for this format. Default None.
    @type service: obj
    @return:
    @rtype: basestring
    @raise TypeError: data passed was not a dict
    """
    if not isinstance(data, dict): 
        raise TypeError("requires type dict.")
    
    opmlitem = []

    # Compose common dictionary elements
    opmlitem.append(
        ("<outline title=\"%(title)s\" text=\"%(text)s\" type=\"%(type)s\" "
        "xmlUrl=\"%(xmlUrl)s\" htmlUrl=\"%(htmlUrl)s\"") % {
            'htmlUrl':data.get("htmlUrl",""),
            'title':data.get("title",""),
            'type':data.get("type",""),
            'xmlUrl':data.get('xmlUrl',""),
            'description':data.get('description',""),
            'text':data.get('text', data['title'])
        })

    # Compose possible dictionary elements
    if data.has_key("imgUrl"):
        opmlitem.append(" imgurl=\"%s\"" % data['imgUrl'])
    
    if data.has_key("altUrl"):
        opmlitem.append(" alturl=\"%s\"" % data['altUrl'])
    
    if data.has_key("subId"):
        opmlitem.append(" subId=\"%s\"" % data['subId'])
    
    if data.has_key("status"):
        opmlitem.append(" status=\"%s\"" % data['status'])
    
    opmlitem.append("/>\n")
    return "".join(opmlitem)
