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
SooVee Serial Audio Manger - Podiobooks transforms for serial audio feeds.  It 
uses compiled regular expressions, lambda expressions to clean raw data from
the Podiobooks.com service.

    - B{Compiled Reg-Ex:} C{PRETITLE}, C{PRESUMMARY}, C{PREEPISODE},
        C{PREIMAGEURL}, C{IMGSOURCE}, C{DELSPACES}, C{LASTTWO}, C{DELHTML}
    - B{Lambda Expressions:} C{toRss(str)}, C{toMB(float)}
    - C{wraptext(line:str, indent:int=None) -> list}

@requires: re
@note: wraptext method should not be here. need to determine better location.
"""
import re

SERVICE = "podiobooks"

#{ Precompiled Regular Expressions used to help format and locate data
PRETITLE = re.compile("^Podiobooks.com: ")
PRESUMMARY = re.compile("^In this podiobook: ")
PREEPISODE = re.compile("^-In this episode: ")
PREIMAGEURL = re.compile("^http://www.podiobooks.com/images/")
IMGSOURCE = re.compile("src=\"(.*?)\"")
DELSPACES = re.compile("[^\w]")
LASTTWO = re.compile("(.*)[\\/](.*)$")
DELHTML = re.compile("<.*?>")

#{ Useful lambda functions to transform values
toRss = lambda x: "%s.rss" % (DELSPACES.sub("", PRETITLE.sub("", x)))
toMB = lambda x: float(x) / 1048576
toKB = lambda x: float(x) / 1024

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
