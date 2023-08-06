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
SooVee Serial Audio Manager - File and path management library for SooVee.

    - C{mkpath(mkpath(filepath:str, workpath:str, subpath:str="") -> str}
    - C{mkfile(urlpath:str) -> str}

@requires: os
@requires: hashlib
"""

def mkpath(filepath, workpath, subpath=""):
    """
    Combine file fragments workpath and filepath. Optionally add a subpath of
    workpath to filepath. When path is new, make needed directories before
    returning the combined path.

    @param filepath: local file path fragment.
    @type filepath: basestring
    @param workpath: local work path fragment.
    @type workpath: basestring
    @param subpath: Optional file path fragement.
    @type subpath: basestring
    @return: Qualified full file path
    @rtype: basestring
    @requires: os
    """
    import os
    pathtofile = os.path.split(filepath)
    workpath = os.path.join(workpath, subpath, pathtofile[0])

    if not os.path.exists(workpath): os.makedirs(workpath)
    
    return os.path.join(workpath, pathtofile[1])


def mkfile(urlpath):
    """
    Create a file path from urlpath to locate a cache file locally. An md5 hash
    is made of urlpath to create the file path that is returned.

    @param urlpath: local file path fragment.
    @type urlpath: basestring
    @return: Qualified file name
    @rtype: basestring
    @requires: hashlib
    """
    from hashlib import md5
    return md5(urlpath).hexdigest()


def mkquery(service, action, idnum):
    """
        Perform a get query on a service page.

        @param service: Intialized soovee.lib.sv_conf.App_Data
        @type service: object
        @param action: Abbreviated name of query to perform.
        @type action: basetring
        @param idnum: Service id of serial audio feed to query.
        @type idnum: int
        @return: Success of query
        @rtype: bool
    """
    from urllib import urlencode
    if idnum.isdigit and action in ['add', 'del', 'one', 'all']:
        action = urlencode({service.QUERYNAME[action]: int(idnum)})
        return service.QUERYURI % action
    else:
        raise KeyError
