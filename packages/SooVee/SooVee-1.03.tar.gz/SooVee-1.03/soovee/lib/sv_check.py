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
SooVee Serial Audio Manger -  Feed update library for SooVee. This updates opml
data and in turn each rss feeds listed.

    - C{Feed(cache:obj, opml:str, store:str, service:obj) -> None}
    - C{Feed.next(None) -> string}
    - C{len(Feed)}
    - C{[item for item in Feed]}

@requires: soovee.lib.sv_data
"""
from sv_data import Data #: Opml / Rss data parsers

class Feed(object):
    """
    Update through iteration of Opml listed Rss feeds.
    
        - C{feed(cache:obj, opml:str, store:str, service:obj) -> None}
        - C{len(feed)}
        - C{[feed for feed in feed(cache, opml, store, service]}
    """
    __index = -1
    def __init__(self, cache, opml, store, service=None):
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
        self._cache, self._store = cache.Cache, store
        self.opml = Data.Opml(
            self._cache(opml, opml.split("/")[-1], 
            workstore=store, update=True).data()
            )
        # Provide missing toRss expression if one is missing or original
        self._toRss = ((lambda x: "%s.rss" % x)
            if service is None or not hasattr(service, toRss)
            else service.toRss)

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
            curFeed = self.opml[self.__index]
            filename = self._toRss(curFeed['title'])
            rssFile = Data.Rss(self._cache(pathname=curFeed['xmlUrl'], 
                filename=filename, workstore=self._store).data())
            
            if not rssFile['eps'][-1].get('description',"") == "The End":
                self._cache(pathname=curFeed['xmlUrl'], filename=filename, 
                    workstore=self._store, update=True)

            return (self.__index, curFeed['title'])
