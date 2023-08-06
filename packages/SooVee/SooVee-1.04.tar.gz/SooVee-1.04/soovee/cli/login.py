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
SooVee Serial Audio Manager - Login support module for the command interface. It 
allows SooVee to authorize itself with a service account.

- C{doAuthorize(service:obj, account:obj, err:str="") -> tuple}

@requires: L{soovee.lib.sv_read}
"""
import soovee.lib.sv_read as CACHEOBJ

def doAuthorize(service, account, err=""):
    """
    Authorize serial audio user against service containing the feeds.
    
    @params service: Initialized soovee.conf.serviceConf object.
    @type service: object
    @params account: Intialized soovee.conf.Account shelf object.
    @type account: object/dict
    @params err: Error string to append to text description presented
    @type err: str
    @returns: tuple of cache, user, password that was accepted
    @rtype: tuple
    """
    from getpass import getpass
    user, password= account.get("user",""), account.get("password","")

    if err:
        print("Error:%s" % error)
        if raw_input("Login into %s account? yes [no]" % service.SITENAME
            ).lower() == "yes":
            user = raw_input("User:")
            password = getpass("Password:")
        else:
            exit()

    else:
        print("Authorizing account with %s." % service.SITENAME)
        if user and password:
            try:
                if CACHEOBJ.Authorize(
                    uri=service.LOGINURI, query=service.mkAuth(user,password)):
                    return (CACHEOBJ, user, password)
            except CACHEOBJ.CacheException as error:
                pass
        else:
            error = "User and password not valid."

    doAuthorize(service, account, err=error)
