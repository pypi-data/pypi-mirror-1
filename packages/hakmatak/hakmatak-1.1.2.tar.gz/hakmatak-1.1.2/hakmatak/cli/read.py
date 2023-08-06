#****************************************************************
# File:      ./hakmatak/cli/read.py
# (c) 2010, http://hakmatak.org, MIT License, ALL RIGHTS RESERVED
#****************************************************************
import sys

# 20091030, this is a temp hack
# if indexer is [...], insist to obtain it via args or a file indexerPath
def _reget_identifier(identifier,args,indexerPath):
    if identifier[-5:] != '[...]':
        return identifier

    indexer = None
    # try to get from an arg
    if (len(args) > 2):
        indexer = args[2]
    # try to get from a file indexerPath
    if indexer == None and indexerPath != None:
        f = open(indexerPath,'r')
        indexer = f.read()
        f.close()
        # remove white spaces
        import re
        indexer = re.sub("\s+","",indexer)

    if indexer == None:
        raise Exception("indexer [...] can not be obtained from either an args or a file.")

    return "%s%s%s%s" % (identifier[0:-5],'[',indexer,']')

def usage():
    pname = sys.argv[0]
    print >> sys.stderr, "Usage: %s [--help] [--cacheDir dir] --type type [--flatten] [--traverse] [--reCache] [--(outputFormat|output) format] [--callback callback] [--(decompressionTopDir|d11nTopDir) dir] [--(decompressionType|d11nType) type] [--indexerPath path] path identifier [indexer]" % (pname)

from hakmatak.worker4r import Worker
from hakmatak.store import ReaderClassFactory as SRCF
from hakmatak.output import WriterClassFactory as OWCF
from hakmatak.w10n import W10n
from hakmatak.cache import FileCache

class Handler:

    def __init__(self,
        workerClass=Worker,
        storeReaderClassFactory=SRCF(),
        outputWriterClassFactory=OWCF(),
        w10n=W10n()
        ):

        self.workerClass = workerClass
        self.storeReaderClassFactory = storeReaderClassFactory
        self.outputWriterClassFactory = outputWriterClassFactory
        self.w10n = w10n

    def do(self):

        import getopt

        try:
            opts, args = getopt.getopt(sys.argv[1:], "", ["help","cacheDir=","type=","outputFormat=","output=","callback=","flatten","traverse","reCache","decompressionTopDir=","d11nTopDir=","decompressionType=","d11nType=","indexerPath="])
        except getopt.GetoptError, err:
            # print help information and exit:
            print >> sys.stderr, str(err) # print like "option -a not recognized"
            usage()
            sys.exit(2)

        # path and identifier are required
        if (len(args) < 2):
            print >> sys.stderr, "path and/or identifier missing"
            usage()
            sys.exit(2)

        # defaults
        cacheDir = None

        w10nType = None
        outputFormat = None

        callback = None
        flatten = False
        traverse = False
        reCache = False

        d11nTopDir = None
        d11nType = None

        indexerPath = None

        for o, a in opts:
            if o == "--help":
                usage()
                sys.exit()
            elif o in ("--cacheDir"):
                cacheDir = a
            elif o == "--type":
                w10nType = a
            elif o == "--outputFormat":
                outputFormat = a
            elif o == "--output":
                outputFormat = a
            elif o == "--callback":
                callback = a
            elif o in ("--flatten"):
                flatten = True
            elif o in ("--traverse"):
                traverse = True
            elif o in ("--reCache"):
                reCache = True
            elif o in ("--decompressionTopDir"):
                d11nTopDir = a
            elif o in ("--d11nTopDir"):
                d11nTopDir = a
            elif o in ("--decompressionType"):
                d11nType = a
            elif o in ("--d11nType"):
                d11nType = a
            elif o in ("--indexerPath"):
                indexerPath = a
            else:
                assert False, "unhandled option"

        if w10nType == None:
            print >> sys.stderr, "type is not specified"
            usage()
            sys.exit(2)

        cache = None
        if cacheDir != None:
            cache = FileCache(cacheDir)

        path = args[0]
        identifier = args[1]

        # a hack to take indexer from args or file
        identifier = _reget_identifier(identifier,args,indexerPath)

        worker = self.workerClass(
            w10nType,
            traverse=traverse,
            flatten=flatten,reCache=reCache,
            callback=callback,outputFormat=outputFormat,
            d11nTopDir=d11nTopDir,
            storeReaderClassFactory=self.storeReaderClassFactory,
            outputWriterClassFactory=self.outputWriterClassFactory,
            w10n=self.w10n,
            cache=cache
            )
        s,mimeType,paramsUsed = worker.get(path,identifier,d11nType=d11nType)
        print >> sys.stderr, "mimeType:",mimeType
        print >> sys.stderr, "paramsUsed:",paramsUsed
        print >> sys.stderr, "cacheDir:",cacheDir
        sys.stdout.write(s)

if __name__ == '__main__':
    Handler().do()
