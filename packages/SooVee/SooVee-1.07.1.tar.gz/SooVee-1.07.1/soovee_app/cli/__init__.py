#!/usr/bin/python
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
SooVee Serial Audio Manager - Intializes the command interface.

    - C{Exec(mode="podiobooks":str, optargs:list=None) => None}

@requires: L{soovee_app.cli.main}
@requires: L{soovee_app.cli.login}
@requires: L{soovee_app.conf}
"""
import login as Auth #: Command login module
import main as Term #: Command interface module
from ..conf import Serviceconf, ACCOUNT #: Service and Account configurations

#
#{ Command interface initialization
#
def Exec(mode="podiobooks", optargs=None):
    """
    Authorize against a serial audio service account. Then intialize the main
    module of the command interface to begin the process of task selection.
    
    @param mode: Service to retrieve serial audio info. Default 'podiobooks'
    @type mode: string
    @param optargs: Optional command line arguments passed.
    @type optargs: list
    @return:
    @rtype: None
    """
    service = Serviceconf(mode)
    account = ACCOUNT

    try:
        #
        #{ Get authorized with serial audio feed service account.
        #
        cache, account['user'], account['password'] = Auth.do_authorize(
        service=service, account=account)
        #
        #{ Show command interface
        #
        Term.main(cache=cache, service=service, account=account,
            command=optargs[0] if optargs else None)

    except KeyboardInterrupt:
        exit("\n\nProgram terminated")


