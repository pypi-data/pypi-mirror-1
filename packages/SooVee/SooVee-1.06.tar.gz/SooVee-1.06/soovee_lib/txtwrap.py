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
SooVee Serial Audio Manger - Line Wrap libary for the SooVee. It will wrap any 
length of text as well as allowing the text to be indented.

    - C{wrapText(line:str, indent:int=None) -> basstring}

"""

def wraptext(line, indent=None):
    """
    Wrap line of text at eighty characters while allowing ability to indent.

    @param line: Text to wrap at 80 characters.
    @type line: basestring
    @param indent: Indent line of text number of characters. Default 'None'.
    @type indent: int
    @return: List of wrapped lines
    @rtype: list
    
    @requires: textwrap
    """
    import textwrap
    indent = " " * indent if indent else ""
    wrapline = textwrap.TextWrapper(width=80, initial_indent=indent,
        subsequent_indent=indent)
    return wrapline.wrap(line)
