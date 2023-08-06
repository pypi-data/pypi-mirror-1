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
SooVee Serial Audio Manager - Caching file reader library for SooVee. This 
allows a file to be read either from the network or locally. If file is present
locally then you must pass 'update=True' to the Cache module.

    - C{Authorize(user:str, password:str) -> bool}
    - C{Cache(pathname:str, filename:str, **options) -> None}
    - C{Cache.data(datatype="r":str) -> [str|bin]}
@requires: os
@requires: cookielib
@requires: urllib2
@requires: urllib
"""
import os
import cookielib
import urllib2
from urllib import urlencode
#
#{ Directory store locations
#
WORKSTORE = os.environ['HOME'] #: Location for feed data
#
#{ Urllib2 http header and cookie setup
#
CONTENTHEADERS = {
    'User-Agent':'Mozilla/5.0 (compatible; Linux i686; en; rv:1.9.0.5)',
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset':'ISO-8859-1,utf-8;q=0.7,*;q=0.7'
    }
cj = cookielib.LWPCookieJar()
WEB_OBJ = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
urllib2.install_opener(WEB_OBJ)

class CacheException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

#
#{ Web cookie authorization
#
def Authorize(uri, query):
    """
    Retrieve auth cookie to recieve access to user's serial audio feed service.

    @param uri: Location of service login page.
    @type uri: basestring
    @param query: Dictionary of query name / value pairs.
    @type query: dict
    @return: Success of operation
    @rtype: boolean
    @raises CacheException: If it encounter connection errors
    """
    auth_request = urllib2.Request(uri, urlencode(query), CONTENTHEADERS)
    #
    #{ Open connection to website
    #
    try: 
        webobj = WEB_OBJ.open(auth_request)
    except urllib2.URLError as error:
        webobj.close()
        raise CacheException("Authentication Error: %s" % error)
    #
    # Verify website authentication
    #
    return False if webobj.geturl() == uri else True #: Same page? Login failed

#
#{ Fetch and cache files
#
class Cache():
    """
    Website data collector.

        - C{Cache(pathname:str, filename:str, **options) -> None}
        - C{Cache.data(datatype:str="r") -> [str|bin]}
    """
    _urlContent = ""
    def __init__(self, pathname, filename, **options):
        """
        Retrieval method for acquiring page data from a website. Caching or
        storing each file. self._urlCheck notifies direct access is available.
        All keyword options are passed on to L{self._cacheData} which manages
        the internet transaction.

        @param pathname: Internet path-filename to retrieve original
        @type pathname: basestring
        @param filename: Local path-filename to store cache
        @type filename: basename
        @param options: post(str), hook(obj), update(bool), data(bool)
        @type options: keywords
        @return:
        @rtype: None
        """
        from sv_file import setName
        self._workFile = setName(filename=filename,
            workstore=options.get("workstore", WORKSTORE), combine=True)
        self._urlCheck = self._cacheData(pathname, self._workFile, **options)

    def _cacheData(self, pathname, filename, **options):
        """
        Caching method for page and file data retrieval. Cache up to 2 MB of
        pathname data in self._urlContent while also writing data to filename.
        Cache filename is accessed first unless keyword option has 'update=True'

        @param pathname: Internet path-filename to retrieve original
        @type pathname: basestring
        @param filename: Local path-filename to store cache
        @type filename: basestring
        @param options: post(str), hook(obj), update(bool), data(bool)
        @type options: keywords
        @return: Data available in self._urlContent.
        @rtype: boolean
        @raises CacheException: If encounters connection error, file errors, or
            data mismatch.
        """
        #print cj
        reporthook = options.get('hook', None) #: Method to monitor progress
        if (not os.path.exists(filename) or options.get('update', False) or
            os.path.getsize(filename) == 0):
            reqObj = urllib2.Request(pathname, options.get('post', None), 
                CONTENTHEADERS)
            #
            # Open connection to website
            #
            try: 
                #print pathname
                webObj = WEB_OBJ.open(reqObj)
                #print webObj.geturl()
            except (urllib2.URLError, urllib2.HTTPError) as error:
                webObj.close()
                raise CacheException("Connection Error: %s" % error)
            self._urlHeaders = webObj.info()
            #print webObj.info()
            #
            # read & write fileObj to filename
            #
            fileObj = open(filename, 'wb')
            blockread, blocksize, filesize = -1, 1024 * 8, 0
            # Set intial progress monitor
            if reporthook:
                filesize = int(self._urlHeaders.get("Content-Length", -1))
                reporthook(blockread, blocksize, filesize)
            # read & write data blocks with storage
            readsize, result = 0, True
            while 1:
                try: block = webObj.read(blocksize)
                except (urllib2.URLError, urllib2.HTTPError) as error:
                    webObj.close()
                    fileObj.close()
                    os.unlink(filename)
                    raise CacheException("Download Error: %s" % error)
                if not block: break
                readsize += len(block)
                try: fileObj.write(block)
                except IOError as error:
                    webObj.close()
                    fileObj.close()
                    os.unlink(filename)
                    raise CacheException("Storage Error: %s" % error)
                blockread += 1
                # Store data block
                if (blockread * blocksize) < (1048576 * 2):
                    self._urlContent += block
                else:
                    self._urlContent, result = None, False
                # Set progress of progress monitor
                if reporthook: reporthook(blockread, blocksize, filesize)
            webObj.close()
            fileObj.close()
            #
            # Raise exception actual size not content-length header
            #
            if filesize >= 0 and readsize < filesize:
                raise CacheException("Download Error: Size Mismatch Found")
        else:
            result = False
        return result

    def data(self, datatype="r"):
        """
        Provide access to an intialized object's data. Data will come either
        from its cache file or the data saved in self._urlContent.

        @param datatype: Option of file open. [r|rb]. Default 'r'.
        @type datatype: basestring
        @return: content of object's cached file
        @rtype: [basestring|bin]
        """

        if not self._urlCheck:
            fileObj = open(self._workFile, datatype)
            self._urlContent = fileObj.read()
            fileObj.close()
        #
        # Data conversion munging for possible unfriendly bytes
        #
        if datatype == "rb":
            import cStringIO
            return cStringIO.StringIO(self._urlContent)
        else:
            return unicode(self._urlContent, encoding="cp1252", errors="ignore")

