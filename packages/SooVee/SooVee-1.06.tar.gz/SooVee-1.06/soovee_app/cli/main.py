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
SooVee Serial Audio Manager - Main support module for the command interface. 
Load on-demand soovee.cli.feed and soovee.cli.page depending on tasks performed.

    - C{Main(cache:object, opmlpath:str, command=None:str) -> None}

@requires: L{soovee.conf}
@requires: L{soovee.cli.feed}
@requires: L{soovee.cli.page}
@requires: L{soovee.cli.entry}
"""
#from ..conf import CACHEDIR
import entry as entry

#
#{ Terminal interface
#
def main(cache, service, account, command=None):
    """
    Provide the command interface to access the many serial audio feed tasks
    available on a service account. Interface presents a series of options to
    select from to perform the tasks. It loops over the task or command option 
    to enable multiple and varied transactions. An empty line will terminate the 
    current task or interface if at the command options.

        - UPDATE - Update serial audio feed data from a service account.
        - FORMAT - Format and output serial audio feeds in a new file.
        - SUBSCRIBE - Add / delete serial audio feeds from service account by
            chosen feed id.
        - RELEASE - Release of one / all episdoes from a serial audio feed on a 
            service account.
        - BROWSE - Create custom files from serial audio info on service's web 
            page.

    @param cacheobj: Initialized soovee.lib.sv_read object.
    @type cacheobj: object
    @param service: Initialized soovee.conf.serviceConf object.
    @type service: object
    @param account: Intialized soovee.conf.Account shelf object.
    @type account: object/dict
    @param command: Command passed from command line. Default None
    @type command: basestring
    @return:
    @rtype: None
    @requires: L{soovee.cli.feed}
    @requires: L{soovee.cli.page}
    @requires: L{soovee.cli.entry}
    """
    opml = service.OPMLURI % account['user']
    cmd_check = True

    while 1:
        #
        #{ Show available commands for serial audio feed service like Podiobooks
        #
        if not command:
            cmd_check, command = entry.choice(
                options=['update', 'format','subscribe', 'release', 'browse'],
                string="Perform Task"
                )
        #
        #{ Update Task -- refresh the serial audio feed cache for a service.
        #
        elif command == "update":
            print("Updating serial audio feed cache.")
            from feed import update
            update(opml=opml, cache=cache, service=service)
            del(update)
            command = None #: Unset selected command.
        #
        #{ Format Task -- write details of the service's account feeds.
        #
        elif command == "format":
            print("Format and write serial audio feeds to a new file.")
            from ..forms import FORMS as forms #: Forms system with plugins
            check, reply = entry.choice(options=forms.list(),
                string="File format")
            del(forms)
            if check:
                directory = account.get("LastDir", None)
                account['LastDir'] = entry.path(directory) or directory
                from feed import compose
                compose(opml=opml, directory=account['LastDir'],
                    form=reply, cache=cache, service=service)
                del(compose)
            else: command = None
        #
        # Subscribe Task -- Add/delete serial audio feeds from a service by id.
        #
        elif command == "subscribe":
            print("Manage serial audio feeds.")
            
            check, reply = entry.choice(options=['add', 'del'],
                string="Edit subscriptions")
            if check:
                check, value = entry.value(length=3 if reply == "add" else 6, 
                    string="For serial audio feed")
                if check:
                    from feed import manage
                    manage(action=reply, idnum=value, cache=cache, 
                        service=service)
                    del(manage)
            else: command = None
        #
        # Release command -- Force one/all service's account feed episodes.
        #
        elif command == "release":
            print("Manage your Podiobooks.com subscription releases.")
            check, reply = entry.choice(options=['one', 'all'],
                string="Release episodes")
            if check:
                check, value = entry.value(length=6, 
                    string="For serial audio feed")
                if check:
                    from feed import manage
                    manage(action=reply, idnum=value, cache=cache, 
                        service=service)
                    del(manage)
            else: command = None
        #
        # Browse command --- Read service's account subscription or search pg.
        #
        elif command == "browse":
            print("Browse and write service web page to a file.")
            print("Choose between Podiobooks: [sub]criptions.php or [all] for "
                "search.php.")
            from ..pages import PAGES as pages
            check, reply = entry.choice(
                options=pages.list(service.SERVICE), 
                string="Which page"
                )
            del(pages)
            if check:
                from ..forms import FORMS as forms
                check, option = entry.choice(options=forms.list("htm"),
                    string="Create format")
                del(forms)
                if check:
                    directory = account.get("LastDir", None)
                    account['LastDir'] = entry.path(directory) or directory
                    from page import browse
                    browse(action=reply, form=option,
                        directory=account['LastDir'], cache=cache,
                            service=service)
                    del(browse)
            else: command = None
        #
        # Exit command --- Exit terminal.
        #
        if not cmd_check:
            break
