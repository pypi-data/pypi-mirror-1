#****************************************************************
# File:      ./hakmatak/output/json.py
# (c) 2010, http://hakmatak.org, MIT License, ALL RIGHTS RESERVED
#****************************************************************
import simplejson as json

from writer import Writer

#MIMETYPE = "application/json"
# this is more browser friendly
MIMETYPE = "text/plain"

class Json(Writer):

    def write(self,d,path=None):
        return (json.dumps(d,indent=4),MIMETYPE)

def main():
    d = {"a":1,"b":"2","c":[1,2]}
    jsonWriter = Json()
    data,mimeType = jsonWriter.write(d)

    import sys
    print >>sys.stderr, mimeType
    print >>sys.stdout, data

if __name__ == "__main__":
    main()
