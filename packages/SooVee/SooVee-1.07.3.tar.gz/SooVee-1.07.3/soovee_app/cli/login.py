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

    - C{do_authorize(service:obj, account:obj, err:str="") -> tuple}

@requires: L{soovee_lib.cache}
@requires: getpass
"""


def do_authorize(service, account, err=""):
    """
    Authorize serial audio user against service containing the feeds. Attempt
    to authorize first and then fall back by passing an error back to method.
    
    @param service: Initialized soovee.conf.serviceConf object.
    @type service: object
    @param account: Intialized soovee.conf.Account shelf object.
    @type account: object/dict
    @param err: Error string to append to text description presented
    @type err: str
    @returns: tuple of cache, user, password that was accepted
    @rtype: tuple
    """
    import soovee_lib.cache as cache
    from getpass import getpass
    user, password = account.get("user",""), account.get("password","")

    if err:
        #{ Method recieved error message, so offer user way to input their info.
        print("Error: %s" % err)
        if raw_input("Login into %s account? yes [no]" % service.SITENAME
            ).lower() == "yes":
            user = raw_input("User:")
            password = getpass("Password:")
        else:
            exit()

    else:
        #{ Method recieved no error message, so attempt with their current info.
        print("Authorizing account with %s." % service.SITENAME)
        if user and password:
            try:
                if cache.authcookie(
                    uri=service.LOGINURI, query=service.MKAUTH(user, password)):
                    return (cache, user, password)
            except cache.CacheException as error:
                pass
        else:
            error = "User and password not valid."

    #{ Call method with an error message
    do_authorize(service, account, err=error)
