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

    - C{Exec(mode="podiobooks":str, optargs=[]:list) => None}

@requires: L{soovee.cli.main}
@requires: L{soovee.cli.login}
@requires: L{soovee.lib.sv_conf}
"""
import login as Auth #: Command login module
import main as Term #: Command interface module
import soovee.conf as Conf

#
#{ Command interface initialization
#
def Exec(mode="podiobooks", optargs=[]):
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
    Service = Conf.serviceConf(mode)
    Account = Conf.Account

    try:
        #
        #{ Get authorized with serial audio feed service account.
        #
        CACHEOBJ, Account['user'], Account['password'] = Auth.doAuthorize(
        service=Service, account=Account)
        #
        #{ Show command interface
        #
        Term.Main(cacheobj=CACHEOBJ, service=Service, account=Account,
            command=optargs[0] if optargs else None)

    except KeyboardInterrupt:
        exit("\n\nProgram terminated")


