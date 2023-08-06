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
SooVee Serial Audio Manager - File and Path munge library for SooVee. It creates
a local file path from path fragments.

    - C{setName(filename:str, workstore:str, combine:bool=False) -> str}

@requires: os
"""
import os

BASESTORE = os.environ['HOME'] #: If set None BASESTORE will be current work dir

def setName(filename, workstore, combine=False):
    """
    Manage local file path fragments by creating a qualified pathname for 
    filename.

    @param filename: local file path.
    @type filename: basestring
    @param workstore: File path fragment to store filename under
    @type workstore: basestring
    @param combine: Should it merge BASESTORE with workstore? Default 'False'.
    @type combine: bool
    @return: qualified full file path
    @rtype: basestring
    """
    pathtofile = os.path.split(filename)
    basestore = BASESTORE or os.getcwd()
    if combine:
        workDir = os.path.join(BASESTORE, workstore, pathtofile[0])
    else:
        workDir = os.path.join(workstore or BASESTORE, pathtofile[0])
    if not os.path.exists(workDir): os.makedirs(workDir)
    return os.path.join(workDir, pathtofile[1])

#def pbmakeline(line):
#    """
#    Encode line of text so we don't generate errors about character encoding.

#    @raise UnicodeEncodeError: On unsuccessful encoding of line.
#    @param line: Line of text
#    @type line: basestring
#    @return:
#    @rtype: basestring
#    """
#    try:
#        return line.encode("ascii", "xmlcharrefreplace")
#    except UnicodeEncodeError, err:
#        print err, "\n", line


