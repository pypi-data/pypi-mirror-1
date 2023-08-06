#****************************************************************
# File:      ./hakmatak/cache.py
# (c) 2010, http://hakmatak.org, MIT License, ALL RIGHTS RESERVED
#****************************************************************
import sys

# the parent class/interface to be subclassed
class Cache:
    # must be overriden
    # get cache by key
    # returns (data,mimeType) or None if not cached
    def get(self,key):
        raise Exception("%s undefined" % sys._getframe().f_code.co_name)

    # must be overriden
    # set cache by key
    # returns a dictionary that is implementation specific
    # or throw exception
    def set(self,key,data,mimeType=None):
        raise Exception("%s undefined" % sys._getframe().f_code.co_name)

# the exception class
class CacheException(Exception):
    pass

# below are some real classes

import os
import md5

# Very Simple File-based Cache Class
# Neither robust nor efficient, mostly used for assisting debugging.
# cache file contains mimeType + "\n" + data

class FileCacheException(CacheException):
    pass

class FileCache(Cache):
    def __init__(self,cacheDir):
        self.cacheDir = cacheDir

    def _get_tag(self,key):
        return md5.new(key).hexdigest()

    def get(self,key):
        tag = self._get_tag(key)
        path = os.path.join(self.cacheDir,tag)

        if not os.path.exists(path):
            return None

        f = open(path,"rb")
        bytes = f.read()
        f.close()

        idx = bytes.find("\n")
        if idx == -1:
            raise FileCacheException("Internal inconsistency.")

        data = bytes[idx+1:]
        mimeType = bytes[:idx]
        return (data,mimeType)

    def set(self,key,data,mimeType=None):
        if data == None:
            raise FileCacheException("Can not cache None.")
        if mimeType == None:
            mimeType = "application/octet-stream"

        tag = self._get_tag(key)
        path = os.path.join(self.cacheDir,tag)

        if not os.path.exists(self.cacheDir):
            os.makedirs(self.cacheDir)

        f = open(path,"wb")
        f.write(mimeType+"\n"+data)
        f.close()

        return {"path":path}

def test():

    cacheDir = '/tmp/w10n';

    fileCache = FileCache(cacheDir)

    key = '/abc.nc/var[]'

    data = "this is a try"
    mimeType = "text/plain"
    rv = fileCache.set(key,data,mimeType=mimeType)
    print >> sys.stderr, rv

    data,mimeType = fileCache.get(key)
    print >> sys.stdout, data
    print >> sys.stderr, mimeType

def main():

    import sys

    """
    if (len(sys.argv) != 2):
        print "Usage: key"
        sys.exit(0)
    """

    test()

if __name__ == '__main__':
    main()
