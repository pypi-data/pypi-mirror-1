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
SooVee Serial Audio Manager - List Iterator library for Soovee. It allows the
iteration of a que list from a specific string found in the list.

    - C{Que(enclosures:list) -> None}
    - C{Que.next(None) -> string}
    - C{Que.set(value:str) -> None}
    - C{[item for item in Que]}
"""

class Que(object):
    """
    Iterable container to play a list of files.
    """
    __index = -1
    def __init__(self, enclosures):
        """
        Set container to a value list of files.
        
        @param enclosures: value list or string values to iterate.
        @type enclosures: basestring
        @return:
        @rtype: None
        """
        self.__list = enclosures

    def __iter__(self):
        """
        Return this iterator object.
        
        @return: Representation of class object.
        @rtype: object
        """
        return self
    
    def __len__(self):
        """
        @return: Length of Episode list
        @rtype: int
        """
        return len(self.__list)

    def next(self):
        """
        Return next string value in value list.
        
        @return: string value at next position in value list.
        @rtype: basestring
        
        @raises StopIteration: End of value list reached.
        """
        self.__index +=1
        if self.__index == len(self.__list):
            raise StopIteration
        else:
            return self.__list[self.__index]

    def set(self, value):
        """
        Set current position in value list by passed file.
        
        @param value: string value in current value list.
        @type value: basestring
        @return:
        @rtype: None
        """
        self.__index = self.__list.index(value)
