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
SooVee Serial Audio Player - This file is the main setup script.
"""

from distutils.core import setup

setup(name="SooVee",
    version='0.9rc3',
    author='Jeremy Austin-Bardo',
    author_email='tjaustinbardo@gmail.com',
    maintainer='',
    maintainer_email='',
    license='GPL v2 only',
    description="SooVee Serial Audio Manager for a serial audio service feed "
        "subscriptions like on Podiobooks. It will manage, update and retrieve "
        "serial audio feeds and their episodes from a user's subscriptions. "
        "Contains both a command and a graphical interface.",
    requires = ['cookielib', 'cStringIO', 'eyeD3', 'os', 'random', 're', 
        'shelve', 'textwrap', 'urllib', 'urllib2', 'wx', 'xml', 'xdg', 
        'ConfigParser'],
    data_files=[
        # Application Documents
        ('/usr/share/doc/soovee',
            ['README', 'LICENSE']
        ),
        # Application Man Pages
        ('/usr/share/man/man1',
            ['manpages/soovee.1.gz', 'manpages/svterm.1.gz', 
            'manpages/svview.1.gz']
        ),
        # Application Menu Item
        ('/usr/share/applications/',
            ['soovee.desktop']),
        # Application Icon Item
        ('/usr/share/pixmaps/',
            ['icons/soovee-32.png', 'icons/soovee-64.png']),
        ],
    scripts=['sv', 'svterm', 'svview'],
    packages=['soovee.lib', 'soovee.gui', 'soovee.cli', 
        'soovee.forms', 'soovee.pages', 'soovee.regex']
    )

