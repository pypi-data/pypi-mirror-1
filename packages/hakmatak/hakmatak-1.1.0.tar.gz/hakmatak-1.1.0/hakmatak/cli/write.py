#****************************************************************
# File:      ./hakmatak/cli/write.py
# (c) 2010, http://hakmatak.org, MIT License, ALL RIGHTS RESERVED
#****************************************************************
import sys

def usage():
    pname = sys.argv[0]
    print >> sys.stderr, "Usage: %s [--help] --type type --data string path identifier" % (pname)

from hakmatak.worker4w import Worker
from hakmatak.store import WriterClassFactory as SWCF

class Handler:

    def __init__(self,
        workerClass=Worker,
        storeWriterClassFactory=SWCF()):

        self.workerClass = workerClass
        self.storeWriterClassFactory = storeWriterClassFactory

    def do(self):

        import getopt

        try:
            opts, args = getopt.getopt(sys.argv[1:], "", ["help","type=","data="])
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

        w10nType = None
        data = None
        for o, a in opts:
            if o == "--help":
                usage()
                sys.exit()
            elif o == "--type":
                w10nType = a
            elif o == "--data":
                data = a
            else:
                assert False, "unhandled option"

        if w10nType == None:
            print >> sys.stderr, "type is not specified"
            usage()
            sys.exit(2)

        path = args[0]
        identifier = args[1]

        worker = self.workerClass(
            w10nType,
            storeWriterClassFactory=self.storeWriterClassFactory
            )
        status = worker.put(path,identifier,data=data)
        print >> sys.stderr, status

if __name__ == "__main__":
    Handler().do()
