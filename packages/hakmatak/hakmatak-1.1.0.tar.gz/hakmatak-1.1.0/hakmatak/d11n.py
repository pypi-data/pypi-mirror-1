#****************************************************************
# File:      ./hakmatak/d11n.py
# (c) 2010, http://hakmatak.org, MIT License, ALL RIGHTS RESERVED
#****************************************************************
import os
import md5

class D11n:
    """Decompression Class
    currently support gzip and bz2 compression types"""
    def __init__(self,topDir):
        self.topDir = topDir
        #if not os.path.exists(self.topDir):
        #    os.mkdir(self.topDir,0755)

    def _de_gzip(self,inPath,outPath):
        import gzip
        fin = gzip.open(inPath, 'rb')
        bytes = fin.read()
        fin.close()
        fout = open(outPath, 'wb')
        fout.write(bytes)
        fout.close()
        return outPath

    def _de_bz2(self,inPath,outPath):
        import bz2
        fin = bz2.BZ2File(inPath, 'rb')
        bytes = fin.read()
        fin.close()
        fout = open(outPath, 'wb')
        fout.write(bytes)
        fout.close()
        return outPath

    def get(self,path,d11nType=None):

        # figure out d11nType from path
        if d11nType == None:
            if path[-4:].lower() == '.bz2':
                d11nType = 'bz2'
            if path[-3:].lower() == '.gz':
                d11nType = 'gzip'

        isDecompressed = False
        if d11nType == None:
            return (path,isDecompressed)

        d11nType = d11nType.lower()

        d11nDir = os.path.join(self.topDir,d11nType)

        tag = md5.new(path).hexdigest()
        d11nPath = os.path.join(d11nDir,tag)

        isDecompressed = True

        # if decompressed before
        if os.path.exists(d11nPath):
            #print "using cache"
            return (d11nPath,isDecompressed)

        if d11nType == 'gzip':
            if not os.path.exists(d11nDir):
                os.makedirs(d11nDir,0755)
            return (self._de_gzip(path,d11nPath),isDecompressed)

        if d11nType == 'bz2':
            if not os.path.exists(d11nDir):
                os.makedirs(d11nDir,0755)
            return (self._de_bz2(path,d11nPath),isDecompressed)

        raise Exception("do not know how to decompress for %s" % d11nType)

def test():
    import getpass

    topDir = os.path.join('/tmp',getpass.getuser(),"d11n");

    d11n = D11n(topDir)

    path = '/usr/share/man/pl/man8/rpm.8.gz'
    d11nPath,isDecompressed = d11n.get(path,'gzip')
    print (d11nPath,isDecompressed)
    print D11n(topDir).get(path,'gzip')

    #path = 'T20010012001008.L3m_8D_SST_4.bz2'

    path = '/usr/share/doc/coreutils-5.97/ChangeLog.bz2'
    print D11n(topDir).get(path,'bz2')

    path = '/bin/bash'
    print D11n(topDir).get(path)
    #print D11n(topDir).get(path,'bz2')

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
