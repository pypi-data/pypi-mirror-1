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
SooVee Serial Audio Manager - Network file access library for SooVee. This 
allows a file to be read once from the network or then locally aftwerwards. If
file is present locally, you must pass 'update=True' to the Cache module.

    - C{Authorize(user:str, password:str) -> bool}
    - C{Cache(pathname:str, filename:str, **options) -> None}
    - C{Cache.data(mode="r":str) -> [str|bin]}

@requires: os
@requires: cookielib
@requires: urllib2
@requires: urllib
@requires: cStringIO
@requires: xdg.BaseDirectory
@requires: {soovee_lib.mkuri}
"""
import os
import cookielib
import urllib2
from urllib import urlencode
from mkuri import mkpath, mkfile

HOMEPATH = os.environ['HOME']

#{ Set default workpath from xdg default directories or under user's homepath
try:
    from xdg.BaseDirectory import xdg_cache_home as WORKPATH
    WORKPATH = os.path.join(WORKPATH, "soovee")

except ImportError:
    WORKPATH = os.path.join(HOMEPATH, ".soovee")

#{ Urllib2 http header
CONTENTHEADERS = {
    'User-Agent':'Mozilla/5.0 (compatible; Linux i686; en; rv:1.9.0.5)',
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset':'ISO-8859-1,utf-8;q=0.7,*;q=0.7'
    }

#{ Setup Urllib2 cookie object
cj = cookielib.LWPCookieJar() # Into WEBOBJ?
WEB_OBJ = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
urllib2.install_opener(WEB_OBJ)


class CacheException(Exception):
    """
    Generic Cache Exception
    """
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

#
#{ Service authorization
#
def authcookie(uri, query):
    """
    Authorize servicr login query with uri. The module will then contain an auth
    cookie to access a user's serial audio feed service.

    @param uri: Location of service login page.
    @type uri: basestring
    @param query: Dictionary of query name / value pairs.
    @type query: dict
    @return: Success of operation
    @rtype: boolean
    @raises CacheException: If it encounter connection errors
    """
    auth_request = urllib2.Request(uri, urlencode(query), CONTENTHEADERS)

    #{ Open connection to website
    try: 
        webobj = WEB_OBJ.open(auth_request)

    except (urllib2.URLError, urllib2.HTTPError) as error:
        webobj.close()
        raise CacheException("Authentication Error: %s" % error)

    # Verify website authentication
    return False if webobj.geturl() == uri else True #: Same page? Login failed

#
#{ Cache mechanisim
#
class Cache():
    """
    Store Internet files locally.

        - C{Cache(urlpath:str, **[filepath:str|workpath:str|post:str|hook:obj|
            update:bool) -> None}
        - C{Cache.data(mode:str="r") -> [str|bin]}
    
    Progress Update Hook
    ====================
        - C{hook(blockread:int, blocksize:int, filesize:int)}
    """
    

    def __init__(self, urlpath, **options):
        """
        Intialize cache file for urlpath. Cache file name will be passed as 
        keyword or created by a md5 hash of urlpath. Working directory can be
        passed as a keyword too to write file to a different location. All 
        keywords are passed on to self._cacheData which manages the transaction.

        @param urlpath: Internet path-filename to retrieve original
        @type urlpath: basestring
        @keyword filepath: Local filepath fragment. (basestring)
        @keyword workpath: Local workpath fragment. (basestring)
        @keyword post: Url-encoded dictionary of values. (basestring)
        @keyword hook: Object that will recieve progress updates. (object)
        @keyword update: Switch to update cache when a local file exists. (bool)
        @return:
        @rtype: None
        
        @requires: L{soovee_lib.mkuri}
        """

        self.url = {"head": "", "body": ""}
        self._workfile = mkpath(options.get("filepath", mkfile(urlpath)), 
            options.get("workpath", WORKPATH))
        self._hook = options.get('hook', None)
        self._cachedata(urlpath, **options)

    def _cachedata(self, urlpath, **options):
        """
        Page and file data retrieval method via caching. Checks for presence in 
        cache prior to internet retrieval from urlpath unless keyword update is 
        passed True or cache file size is zero. Up to 2 MB retrieved is stored 
        in memory, while also writing retrieved to cache file, self._workfile. 
        If hook is present, progress feedback is given.

        @param urlpath: Internet path-filename to retrieve original
        @type urlpath: basestring
        @keyword post: Url-encoded dictionary of values. (basestring)
        @keyword hook: Object that will recieve progress updates. (object)
        @keyword update: Switch to update cache when a local file exists. (bool)
        @return: Data available in self._urlContent.
        @rtype: boolean
        @raises CacheException: If encounters connection error, file errors, or
            data mismatches.
        @requires: urllib2
        """
        if (not os.path.exists(self._workfile) or options.get('update', False) 
            or os.path.getsize(self._workfile) == 0):

            #{ Open connection to website
            try: 
                webobj = WEB_OBJ.open(urllib2.Request(urlpath, 
                    options.get('post', None), CONTENTHEADERS))

            except (urllib2.URLError, urllib2.HTTPError) as error:
                webobj.close()
                raise CacheException("Connection Error: %s" % error)

            self.url['head'] = webobj.info()

            #{ read & write fileObj to filename
            fileobj = open(self._workfile, 'wb')
            blockread, blocksize, filesize = int(-1), int(1024 * 8), int(0)

            #{ Set intial progress monitor
            if self._hook:
                filesize = int(self.url['head'].get("Content-Length", -1))
                self._hook(blockread, blocksize, filesize)

            #{ read & write data blocks with storage
            readsize = 0
            while 1:
                try: block = webobj.read(blocksize)
                except (urllib2.URLError, urllib2.HTTPError) as error:
                    webobj.close()
                    fileobj.close()
                    os.unlink(self._workfile)
                    raise CacheException("Download Error: %s" % error)

                if not block: break

                readsize += len(block)

                try: fileobj.write(block)
                except IOError as error:
                    webobj.close()
                    fileobj.close()
                    os.unlink(self._workfile)
                    raise CacheException("Storage Error: %s" % error)

                blockread += 1
                
                #{ Store data block up to 2 mb
                if (blockread * blocksize) < (1048576 * 2):
                    self.url['body'] += block 
                else: self.url['body'] = None

                #: Set progress of progress monitor
                if self._hook: self._hook(blockread, blocksize, filesize)

            webobj.close()
            fileobj.close()

            #{ Raise exception actual size not content-length header
            if filesize >= 0 and readsize < filesize:
                os.unlink(self._workfile)
                raise CacheException("Download Error: Size Mismatch Found")

        return bool(self.url['body'])

    def data(self, mode="r"):
        """
        Provide access to an intialized object's data. Data will come either
        from its cache file or the data saved in self._urlContent.

        @param mode: Option of file open. [r|rb]. Default 'r'.
        @type mode: basestring
        @return: content of object's cached file
        @rtype: [basestring|bin]
        @requires: cStringIO
        """
        if not self.url['body']:
            with open(self._workfile, mode) as data:
                self.url['body'] = data.read()

        #{ Data conversion munging for possible unfriendly bytes
        if mode == "rb":
            from cStringIO import StringIO
            return StringIO(self.url['body'])

        else:
            return unicode(self.url['body'], encoding="cp1252", errors="ignore")

