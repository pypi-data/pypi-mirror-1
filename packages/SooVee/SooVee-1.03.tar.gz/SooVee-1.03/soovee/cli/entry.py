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
SooVee Serial Audio Manager - Entry support module for the command inface. It 
presents a string to the terminal and waits for the response.

    - {choice(options:list, string:str) -> tuple}
    - {directory(directory:str) -> basestring}
    - {feed(length:int) -> tuple}
"""

# Default command entry lambda expression
_entry = lambda s, o: raw_input("%s: [%s] " % (
    s, " | ".join(o) if isinstance(o, list) else o)
    )

def choice(options, string):
    """
    Provide standard input and verification of an option selection.

    @param options: List of accepted options.
    @type options: list
    @param string: Description of selection.
    @type string: basestring
    @return: Selection validity and lowercased value.
    @rtype: tuple
    """
    reply = _entry(string, options)
    return (reply.lower() in options, reply.lower())

def directory(directory):
    """
    Provide standard input format for directory selection. 

    @param directory: Directory to be used as default. None value will be '~/'
    @type string: basestring
    @return: Directory selected.
    @rtype: basestring
    """
    return _entry(
        "Save file to folder", directory or "Default ~"
        ) or directory

def feed(length):
    """
    Provide standard input format for feed id entry.

    @param length: Accepted length of value.
    @type int: basestring
    @return: Value validity and value.
    @rtype: tuple
    """
    reply = _entry("For serial audio feed", "#" * length)
    return (all(reply.isdigit(),len(reply) == length), reply)

