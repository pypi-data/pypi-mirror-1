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
SooVee Serial Audio Manager - Web queries library for Soovee. This perform GET
based queries on a service webpage.

    - C{query(cache:obj, service:obj action:str, idnum:int) -> bool}
    
@note: needs a look to see if this needs moving to sv_read.
"""

def query(cache, service, action, idnum):
    """
        Perform a get query on a service page.
        
        @param cache: Intialized soovee.lib.sv_read object
        @type cache: object
        @param service: Intialized soovee.lib.sv_conf.App_Data
        @type service: object
        @param action: Abbreviated name of query to perform.
        @type action: basetring
        @param idnum: Service id of serial audio feed to query.
        @type idnum: int
        @return: Success of query
        @rtype: bool
    """
    idnum = idnum.strip()
    if idnum.isdigit and action in ['add', 'del', 'one', 'all']:
        action = urlencode({service.QUERYNAME[action]: int(idnum)})

        try:
            cache.Cache(pathname=service.QUERYURI % action, 
            filename="sv%squery.html" % action, update=True)
            
        except cache.CacheException as error:
            return False
            
        return True
        
    else:
        return False
