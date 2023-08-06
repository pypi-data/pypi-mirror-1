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
module plugin. It will create a detailed page containing a section for set of 
serial audio feeds.

    - C{Format.write(filename:str, workstore:str, data:list, cache=None:obj, 
        rx=None:obj) -> None}
    - C{Format.item(item:dict, feed={}:dict, rx=None:obj) -> None}

@requires: L{soovee.lib.sv_data}
@requires: L{soovee.lib.sv_file}
@requires: L{soovee.lib.sv_wrap}
@requires: L{soovee.conf}
"""
METHOD = ("frm","inftxt") #: Tuple of type and format
FILENAME = "svinfo.txt" #: Default file name for page

def write(filepath, workpath, data, cache=None, service=None):
    """
    Initialize and write a detailed text page. The passed Opml data is used 
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
    if not isinstance(data, list): 
        raise TypeError("FormsWrite missing list.")

    from soovee_lib.parse import Xml#: Rss data parsers

    fileobj = open(cache.mkpath(filepath=filepath, workpath=workpath), "w")

    for opml in data:
        yield opml['title']
        
        #{ Read data for feed section
        rss = Xml.rss(cache.Cache(opml['xmlUrl']).data())
        
        #{ Write data for feed section
        fileobj.write(item(
                opml, rss, service).encode("ascii", "xmlcharrefreplace")
            )
    fileobj.close()

def item(data, feed=None, service=None):
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
    if not isinstance(data, dict) and not isinstance(feed, dict): 
        raise TypeError("FormsItem missing dictionaries.")

    from soovee_lib.txtwrap import wraptext #: Line wrapper

    #{ Compose summary header data
    page = ["=" * 80,
        "\n".join(
            wraptext("FEED TITLE: %s" % (
                service.PRETITLE.sub("", data['title'])
            ))),
        "\n".join(
            wraptext("FEED PAGE: %s " % data['htmlUrl'])
            ),
        "\n".join(
            wraptext(service.DELHTML.sub("",data['description']))
            )
        ]

    #{ Compose each episode's data
    for episode in feed['eps']:
        audiofile = "%s (%.2f MB)" % (episode['enclosure']['url'],
            service.TOMB(episode['enclosure']['length']))
        subpage = ["-" * 80,
            "\n".join(
                wraptext("EPISODE TITLE: %s" % episode['title'], 4)
                ),
            "\n".join(
                wraptext("EPISODE AUTHOR: %s" % episode['itunes:author'], 4)
                ),
            "\n".join(
                wraptext("EPISODE CATEGORY: %s" % episode['category'], 4)
                ),
            "\n".join(
                wraptext("EPISODE AUDIOFILE: %s" % audiofile, 4)
                ),
            "\n".join(
                wraptext(
                    service.PREEPISODE.sub("", episode['description']), 4)
                ),
            ]
        page.append("\n".join(subpage))

    return "\n".join(page)
