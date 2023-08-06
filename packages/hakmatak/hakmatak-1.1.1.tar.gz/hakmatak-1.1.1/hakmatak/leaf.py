#****************************************************************
# File:      ./hakmatak/leaf.py
# (c) 2010, http://hakmatak.org, MIT License, ALL RIGHTS RESERVED
#****************************************************************
from constant import ATTRS
from constant import NAME
from constant import DATA

#class Leaf(object):
class Leaf:
    """Leaf Class"""

    _m = {"name":NAME,"attrs":ATTRS,"data":DATA}

    def __init__(self,name):
        self.__dict__["name"] = name
        self.__dict__["attrs"] = []
        self.__dict__["data"] = None

    def __setattr__(self, attr, value):
        if attr not in self._m.keys():
            raise AttributeError, attr + " not allowed"
        self.__dict__[attr] = value

    def __getattr__(self, attr):
        if attr not in self._m.keys():
            raise AttributeError, attr + " non-existent"
        return self.__dict__[attr]

    def get_meta(self):
        d = {}
        for attr in self._m.keys():
            if attr == "data":
                continue
            d[self._m[attr]] = self.__dict__[attr]
        return d

    def get_data(self):
        d = {}
        attr = "data"
        d[self._m[attr]] = self.__dict__[attr]
        return d

    def get(self):
        d = {}
        for attr in self._m.keys():
            d[self._m[attr]] = self.__dict__[attr]
        return d

def test():

    node = Leaf("myLeaf")
    print dir(node)

    print node.name
    print node.attrs
    print node.data

    print node.get_meta()
    print node.get_data()
    print node.get()

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
