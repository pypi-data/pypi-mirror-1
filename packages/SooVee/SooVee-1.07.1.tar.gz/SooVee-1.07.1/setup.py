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
    version='1.07.1',
    author='Jeremy Austin-Bardo',
    author_email='tjaustinbardo@gmail.com',
    maintainer='',
    maintainer_email='',
    license='GPL v2 only',
    url="http://soovee.ausimage.us",
    description="SooVee Serial Audio Manager for a serial audio feed "
        "subscription service.",
    long_description="Serial audio manager for a serial audio service feed"
        "subscription service like Podiobooks. It will manage, update and "
        "retrieve serial audio feeds and their episodes from an account on "
        "services providing an Opml feed subscription list. Contains both a "
        "command and a graphical interface.",
    requires = ['cookielib', 'cStringIO', 'eyeD3', 'os', 'random', 're', 
        'shelve', 'textwrap', 'urllib', 'urllib2', 'wx', 'xml', 'xdg', 
        'hashlib'],
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
    scripts=['soovee', 'svterm', 'svview'],
    packages=['soovee_lib', 'soovee_app.gui', 'soovee_app.cli', 'soovee_app',
        'soovee_app.forms', 'soovee_app.pages', 'soovee_app.conf'],
    keywords="Audio, Opml, Rss, Serial Audio Service, Manager, Viewer, Player",
    platforms="Ubuntu 9.04 (others may work as well)",
    classifiers=[
        'Development Status :: 4 - Beta', # 5 - Production/Stable
        'Environment :: Console',
        'Environment :: X11 Applications',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.6',
        'Topic :: Internet',
        'Topic :: Multimedia :: Sound/Audio',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing :: Markup :: XML',
        ]
    )

