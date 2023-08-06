#****************************************************************
# File:      ./hakmatak/node.py
# (c) 2010, http://hakmatak.org, MIT License, ALL RIGHTS RESERVED
#****************************************************************
from constant import ATTRS,NODES,LEAVES
from constant import NAME

#class Node(object):
class Node:
    """Node Class"""

    _m = {"name":NAME,"attrs":ATTRS,"nodes":NODES,"leaves":LEAVES}

    def __init__(self,name):
        self.__dict__["name"] = name
        self.__dict__["attrs"] = []
        self.__dict__["nodes"] = []
        self.__dict__["leaves"] = []

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
            d[self._m[attr]] = self.__dict__[attr]
        return d

    #def get_data(self):
    #    raise Exception, "get_data() not defined"

    #def get(self):
    #    raise Exception, "get() not defined"

def test():

    node = Node("myNode")
    print dir(node)

    print node.name
    print node.attrs
    print node.nodes
    print node.leaves

    print node.get_meta()

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
