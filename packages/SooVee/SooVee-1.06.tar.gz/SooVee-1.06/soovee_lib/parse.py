#
# (c) 2009 Jeremy AustinBardo <tjaustinbardo AT gmail DOT com>
# Special thanks Marius Gedminas <marius AT gedmin DOT as> for his suggestions.
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
SooVee Serial Audio Manager - Xml feed library for SooVee. This parses xml 
tagged data into a dictionary of nested elements. It also contains an Opml and 
Rss filter to extract the correct node(s).

    - C{Xml(xmldata:str) -> None}
    - C{Xml.children(node:str, brake:str=None) -> str}
    - C{Opml(opml:str)  -> list}
    - C{Rss(rss:str)  -> list}

@requires: xml.dom.minidom
"""
import xml.dom.minidom as mindom

#
#{ Basic dictionay based data node parser
#
class Xml():
    """
    Xml data parser for serial audio data in Opml and Rss.
    
        - C{PbXml(xmldata:stre) -> None}
        - C{PbXml.children(node:str, brake=None:str) -> str}
    """
    def __init__(self, xmldata):
        """
        Get Xml data from initialized soovee.lib.sv_read object and process for
        its nodes and attributes with xml.dom.minidom.

        @param xmldata: Raw unparsed Xml data.
        @type xmldata: str
        @return: 
        @rtype: None
        """
        self._nodedata = mindom.parseString(
                xmldata.encode('ascii','xmlcharrefreplace')
                )


    @staticmethod
    def opml(data):
        """
        Parse a serial audio Opml collection of feeds like Podiobooks. 

            - B{Possible attributes:} title, text, type, xmlUrl, htmlUrl, 
                description

        @param opml: Raw unparsed Ompl file data
        @type opml: basestring
        @return: List of node dictionaries in Opml data
        @rtype: list
        """
        xml = Xml(data)
        nodedata = xml.children("outline", None)
        # List is always unorderd so we sort it
        nodedata.sort(key=lambda x: x['title'].lower())
        return nodedata

    @staticmethod
    def rss(data):
        """
        Parse a serial audio RSS feed like Podiobooks. 

            - B{Possible Summary tags:} title, link, description, webMaster, 
                pubDate, managingEditor, category*, copyright, language, docs,
                generator, image (url, width, height, link, title), atom:link 
                (href, rel, type), itunes:block, itunes:subtitle,
                itunes:summary, itunes:author, itunes:explicit, 
                itunes:image (href), itunes:owner, itunes:email, itunes:name,
                itunes:category (itunes:category (text))

            - B{Possible Item tags:} title, link, comments, description,
                category*, pubDate, author, guid (isPermaLink), 
                enclosure (url, length,type), itunes:author, itunes:subtitle,
                itunes:summary, itunes:explicit, itunes:duration, 
                itunes:keywords

        * category despite multiple tags will return a single combined value.

        @param rss: Raw unparsed Rss file data
        @type rss: basestring
        @return: List of node dictionaries in Rss data
        @rtype: list
        """
        xml = Xml(data)
        nodedata = {"sum":{}, "eps":[]}
        # Parse the website rss feed for summary of audiobook (items).
        nodedata['sum'] = xml.children('channel','item')[0]
        # Parse the website rss feed for episodes of audiobook (items).
        nodedata['eps'] = xml.children('item')
        nodedata['eps'].reverse()
        return nodedata

    def _textnode(self, branch):
        """
        Parse branch for text data by checking for the TEXT_NODE type on nodes.

        @param branch: Xml branch object with CDATA.
        @type branch: xml.dom.minidom
        @return: CDATA value
        @rtype: basestring
        """
        lines = []
        try:
            lines = [node.data 
                for node in branch if node.nodeType == node.TEXT_NODE
                ]
        except TypeError:
            pass
        return "\n".join(lines)

    def _attrnode(self, node):
        """
        Parse element node for its attributes. Node is checked prior to call.

        @param node: Xml node object with attribute value.
        @type node: xml.dom.minidom
        @return: text cdata value
        @rtype: dict
        """
        details = {}
        for attr in range(0, node.attributes.length): 
            attribute = node.attributes.item(attr)
            details[attribute.name] = attribute.value
        return details

    def _elemnode(self, node, brake=None):
        """
        Parse node for data. Check each node for text and attributes assigning
        them to their element or attribute name, nesting names if needed.

        @param node: Xml node object with additional elements.
        @type node: xml.dom.minidom
        @param brake: Value that halts checking elements. Default 'None'.
        @type brake: basestring
        @return: value of elements and their attributes and CDATA
        @rtype: dict
        """
        details = {}
        category = []
        for elem in node.childNodes:
            if elem.nodeType == elem.ELEMENT_NODE:
                #
                # Parse an ELEMENT_NODE eg. <tagname>
                #
                etag = elem.tagName
                if brake and etag == brake: 
                    break #: Halt node parse
                if etag == "category": #: Contains many tags
                    category.append(self._textnode(elem.childNodes))
                else:
                    if elem.hasAttributes():
                        # Parse ELEMENT_NODE attributes and child TEXT_NODES
                        details[etag] = {}
                        details[etag][etag] = self._textnode(elem.childNodes)
                        details[etag] = self._attrnode(elem)
                    if elem.hasChildNodes():
                        # Parse ELEMENT_NODE for child nodes
                        echild = elem.childNodes
                        if node.ELEMENT_NODE in [c.nodeType for c in echild]:
                            details[etag] = self._elemnode(elem)
                            continue
                        elif echild[0].nodeType == node.TEXT_NODE:
                            details[etag] = self._textnode(echild)
                        elif echild[0].nodeType == node.CDATA_SECTION_NODE:
                            details[etag] = echild[0].data
            elem.unlink()
        if category: 
            details['category'] = "; ".join(category)
        return details

    def children(self, node, brake=None):
        """ Parse Xml data for children of a particular node element.
        
        @param node: Name of node to locate
        @type node: basestring
        @param brake: Value that halts checking elements. Default None.
        @type brake: basestring
        @return: List of node dictionaries
        @rtype: list
        """
        nodedata = []
        for item in self._nodedata.getElementsByTagName(node):
            if item.hasAttributes():
                details = self._attrnode(item)
                item.unlink()
            if item.hasChildNodes():
                details = self._elemnode(item, brake)
            if details: 
                nodedata.append(details)
        return nodedata

class Refresh(object):
    """
    Update through iteration of Opml listed Rss feeds.
    
        - C{feed(cache:obj, opml:str, store:str, service:obj) -> None}
        - C{len(feed)}
        - C{[feed for feed in feed(cache, opml, store, service]}
    """
    __index = -1
    def __init__(self, cache, path, **options):
        """
        Update Opml Data in preparation for updating Rss Data.

        @param cache: Initialized soovee.lib.sv_read object.
        @type cache: object
        @param service: Initialized soovee.conf.serviceConf object.
        @type service: object
        @param opml: Service account opml uri
        @type opml: basestring
        @param store: Cache dir to store feeds.
        @type store: basestring
        @return:
        @rtype: None
        """
        self._cache = cache.Cache
        self.opml = Xml.opml(self._cache(path, update=True).data())


    def __iter__(self):
        """
        Return this iterator object.
        
        @return: Representation of class object.
        @rtype: obj
        """
        return self

    def __len__(self):
        """
        @return: Length of Opml data list
        @rtype: int
        """
        return len(self.opml)

    def next(self):
        """
        Update Rss Data based on uri found in Opml Data. 

        @return: Opml data list index, and its feed title.
        @rtype: obj
        """
        self.__index += 1
        if len(self) == self.__index:
            raise StopIteration
        
        else:
            curfeed = self.opml[self.__index]
            rssfile = Xml.rss(self._cache(curfeed['xmlUrl']).data())
            
            if not rssfile['eps'][-1].get('description',"") == "The End":
                self._cache(curfeed['xmlUrl'], update=True)

            return (self.__index, curfeed['title'])
