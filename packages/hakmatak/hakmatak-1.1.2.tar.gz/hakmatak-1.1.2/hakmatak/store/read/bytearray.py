#****************************************************************
# File:      ./hakmatak/store/read/bytearray.py
# (c) 2010, http://hakmatak.org, MIT License, ALL RIGHTS RESERVED
#****************************************************************
"""View a file as a multi-dimensional byte array.
It maps all bytes in a file into an arrary of n dimensions as a w10n tree,
where n is the smallest integer for which file.size <= DIM_LEN^n.
DIM_LEN is a pre-defined integer.
Memebers of inner-most dimension are considered as leaves.
Memebers of all other dimensions are nodes.
Name of either node or leaf is just the byte offset for that entity.
"""

import os

from hakmatak.constant import NAME,VALUE
from hakmatak.constant import DATA

from hakmatak.node import Node
from hakmatak.leaf import Leaf

from reader import Reader
from reader import ReaderException

# length of each dimension, fixed
DIM_LEN = 64

class ByteArray(Reader):

    def __init__(self, path):
        # set self.path
        Reader.__init__(self, path)

        # file size
        self.size = os.stat(path).st_size

        # figure out number of dimensions (nod)
        nod = 0
        tmp = 1
        while tmp < self.size:
            nod += 1
            tmp *= DIM_LEN
        self.nod = nod

    #...............
    # deal with meta

    def _get_meta(self,name):
        tmp = name.split("/")

        level = len(tmp)
        # it is a leaf
        if level == self.nod:
            leafName = tmp[-1]
            leaf = Leaf(leafName)
            return leaf.get_meta()

        # it is a node
        nodeName = tmp[-1]
        if nodeName == "":
            offset = 0
        else:
            offset = int(nodeName)

        a = []
        length = DIM_LEN**(self.nod-level)
        for i in range(DIM_LEN):
            x = offset+i*length
            if x >= self.size:
                break
            a.append({NAME:"%s" % x})

        node = Node(nodeName)
        if self.nod-level == 1:
            node.leaves = a
        else:
            node.nodes = a
        return node.get_meta()

    def get_meta(self,name,traverse=False):
        if traverse == True:
            raise ReaderException("Traverse is not supported.")
        return self._get_meta(name)

    #...............
    # deal with data

    def _get_data(self,name):
        tmp = name.split("/")
        leafName = tmp[-1]
        offset = int(leafName)
        fd = os.open(self.path, os.O_RDONLY)
        os.lseek(fd, offset, 0)
        data = os.read(fd, DIM_LEN)
        os.close(fd)
        return data

    def get_data(self,name,indexer=None,flatten=False):
        return {DATA:self._get_data(name)}
