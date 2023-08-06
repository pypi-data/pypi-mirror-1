#****************************************************************
# File:      ./hakmatak/store/read/reader.py
# (c) 2010, http://hakmatak.org, MIT License, ALL RIGHTS RESERVED
#****************************************************************
import sys

from hakmatak.identifier import META,DATA
from hakmatak.identifier import Identifier

class ReaderException(Exception):
    pass

class Reader:
    # by default, can NOT handle compressed file internally
    canDecompress = False

    # path: path of the store
    def __init__(self,path):
        self.path = path

    # must be overriden
    # name: full name of the intended inner component
    # traverse: if true, visit every descendant
    def get_meta(self,name,traverse=False):
        raise Exception("%s undefined." % sys._getframe().f_code.co_name)

    # must be overriden
    # name: full name of the intended inner component
    # indexer: indexer of an data identifier
    # flatten: if data is an array, whether to flatten it
    def get_data(self,name,indexer=None,flatten=False):
        raise Exception("%s undefined." % sys._getframe().f_code.co_name)

    # can be overriden
    # returns a python dictionary
    def get(self,identifier,traverse=False,flatten=False):
        id7r = Identifier(identifier)

        if id7r.type == META:
            d = self.get_meta(id7r.name,traverse=traverse)
            return (d,id7r.type)

        if id7r.type == DATA:
            d = self.get_data(id7r.name,indexer=id7r.indexer,flatten=flatten)
            return (d,id7r.type)

        raise Exception("Read is not supported for %s." % identifier)
