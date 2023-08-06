#****************************************************************
# File:      ./hakmatak/output/raw.py
# (c) 2010, http://hakmatak.org, MIT License, ALL RIGHTS RESERVED
#****************************************************************
from hakmatak.constant import DATA

from writer import Writer

MIMETYPE = "application/octet-stream"

class Raw(Writer):

    def write(self,d,path=None):
        if not d.has_key(DATA):
            raise Exception("Internal inconsistency: %s missing." % DATA)
        mimeType = MIMETYPE
        data = d[DATA]
        from hakmatak.util.magic import Magic
        m = Magic(mime=True)
        mimeType = m.from_buffer(data)
        return (data,mimeType)

def main():
    d = {DATA:"this is a try"}
    rawWriter = Raw()
    data,mimeType = rawWriter.write(d)

    import sys
    print >>sys.stderr, mimeType
    print >>sys.stdout, data

if __name__ == "__main__":
    main()
