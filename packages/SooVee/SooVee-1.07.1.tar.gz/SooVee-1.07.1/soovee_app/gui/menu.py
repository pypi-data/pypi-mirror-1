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
SooVee Serial Audio Manager - Menu service layout library for SooVee. Value 
MENUBAR holds a lambda expression that allows parent and commands to be passed
into Menu without having to pass the entire menu structures.

    -C {MENUBAR(parent, commands) -> None}

@newfield announce: Announce with TRANSCIEVER
@newfield response: Response for TRANSCIEVER
@newfield handle: Handle wx.Event

@requires: wx
"""
import wx 

class Menu(wx.MenuBar):
    """
    Create menu system by parsing a tuple list of labels and commands.
    
        - C{Menubar(parent:obj, menu:tuple) -> None}
    """
    def __init__(self, parent, menu):
        """
        Initialize menu system with passed menu tuple list.
        
        @param parent: wx parent object
        @type parent: type
        @param menu: menu layout with label to command pairing.
        @return:
        @rtype: None
        """
        wx.MenuBar.__init__(self)
        self._parent = parent

        for title, submenu in menu:
            self.Append(self._buildmenus(submenu), title)

    def _buildmenus(self, submenu):
        """
        Create a single menu in the system by parsing the passed submenu tuple.
        Bind commands found in submenu tuple to corresponding menu events.
        
        @param submenu: menu layout with label to command pairing.
        @type submenu: tuple
        @return: wx.Menu Object.
        @rtype: object
        """
        menuobj = wx.Menu()

        for item in submenu:
            if not item: #allow now to add separators
                menuobj.AppendSeparator()
                continue
            _id = wx.NewId()
            
            #{ Handle new menu request
            if len(item) == 2 and isinstance(item[1], list):
                title, action = item
                menuobj.AppendMenu(_id, title, self._buildmenus(action))
            
            #{ Handle new item request
            elif len(item) == 3 and isinstance(item[1], object):
                title, action, statustext = item
                menuobj.Append(_id, title, statustext)
                wx.EVT_MENU(self._parent, _id, action)

        return menuobj

def __about(self, event):
    """
    Create an about box for soovee.
    
    @param event: Ingnored wx.Event object
    @param event: object
    @return: 
    @rtype: None
    """
    description = ("Manage and perfom many tasks of your serial audio "
        "service account right from the desktop.View individual feeds; Play"
        " or download episodes; Update contents from your account.")
    licence = ("This program is free software; you can redistribute it "
        "and/or modify it under the terms of the GNU General Public License"
        " as published by the Free Software Foundation; version 2 only of "
        "the License.\r\n"
        "This program is distributed in the hope that it will be useful,"
        " but WITHOUT ANY WARRANTY; without even the implied warranty of "
        " MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the "
        " GNU General Public License for more details.\r\n"
        "You should have received a copy of the GNU General Public License"
        "along with this program; if not, write to the Free Software"
        "Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  "
        "02111-1307  USA")

    info = wx.AboutDialogInfo()

    info.SetIcon(wx.Icon("/usr/share/pixmaps/soovee-64.png",
        wx.BITMAP_TYPE_PNG))
    info.SetName('Soovee Serial Audio Manager')
    info.SetVersion('1.07')
    info.SetDescription(description)
    info.SetCopyright('(C) 2009 Jeremy Austin-Bardo')
    info.SetWebSite('http://soovee.ausimage.us')
    info.SetLicence(licence)
    info.AddDeveloper('Jeremy Austin-Bardo')
    #info.AddDocWriter('Jeremy Austin-Bardo')
    #info.AddArtist('Jeremy Austin-Bardo')

    wx.AboutBox(info)

#{ Initialize menu bar for soovee gui
MENUBAR = lambda p, c:Menu(parent=p, menu=[
    ('&Feeds', [
        ('&Update Subscriptions', c['update'], ""),
        ('&Download Episodes', c['download'], ""),
        ('&Exit', lambda x:p.Close(), ""),
    ]),
    ('&Help', [
        ('&About', __about, ""),
    ])
    ])
