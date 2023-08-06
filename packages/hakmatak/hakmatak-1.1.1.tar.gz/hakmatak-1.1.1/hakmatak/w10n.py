#****************************************************************
# File:      ./hakmatak/w10n.py
# (c) 2010, http://hakmatak.org, MIT License, ALL RIGHTS RESERVED
#****************************************************************
from constant import SPEC,APP_NAME,APP_VERSION
from constant import NAME,VALUE

class W10n:

    _l = ["spec",
        "application",
        "type",
        "path",
        "identifier"
        ]

    """
    _m = {"spec":"Specification Version",
        "appName":"Application Name",
        "appVersion":"Application Version",
        "type":"type",
        "path":"path",
        "identifier":"identifier"
        }
    """

    def __init__(self):
        self.__dict__["spec"] = SPEC
        self.__dict__["application"] = "%s-%s" % (APP_NAME,APP_VERSION)
        self.__dict__["type"] = None
        self.__dict__["path"] = None
        self.__dict__["identifier"] = None

    def __setattr__(self, attr, value):
        if attr not in self._l:
            raise AttributeError, attr + " not allowed"
        self.__dict__[attr] = value

    def __getattr__(self, attr):
        if attr not in self._l:
            raise AttributeError, attr + " non-existent"
        return self.__dict__[attr]

    def from_list(self,l):
        for x in l:
            name = x[NAME]
            value = x[VALUE]
            #print name,value
            # skip unrecognized name
            if name not in self._l:
                continue
            self.__dict__[name] = value

    def to_list(self):
        l = []
        for x in self._l:
            if self.__dict__[x] == None:
                continue
            l.append({NAME:x,VALUE:self.__dict__[x]})
        return l

    def to_dict(self):
        d = {}
        for x in self._l:
            if self.__dict__[x] == None:
                continue
            d[x] = self.__dict__[x]
        return d

def test():

    w10n = W10n()

    print w10n.spec
    print w10n.application
    print w10n.type
    print w10n.path
    print w10n.identifier

    print w10n.to_list()
    print w10n.to_dict()

    print ""
    w10n.type = "tar"
    w10n.path = "/this/is/a/try.tar"
    print w10n.to_list()
    print w10n.to_dict()

    print ""
    l = [
        {NAME:"type",VALUE:"zip"},
        {NAME:"path",VALUE:"/another/try.zip"},
        {NAME:"identifier",VALUE:"/me/too/"},
        ]

    w10n.from_list(l)
    print w10n.to_list()
    print w10n.to_dict()

def main():

    """
    import sys

    if (len(sys.argv) != 2):
        print "Usage: key"
        sys.exit(0)
    """

    test()

if __name__ == '__main__':
    main()
