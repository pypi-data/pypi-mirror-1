#****************************************************************
# File:      ./hakmatak/store/write/writer.py
# (c) 2010, http://hakmatak.org, MIT License, ALL RIGHTS RESERVED
#****************************************************************
import sys

from hakmatak.identifier import META,DATA
from hakmatak.identifier import Identifier

class Writer:

    def __init__(self,path):
        self.path = path

    # must be overriden by subclass
    def put_data(self,name,indexer=None,data=None):
        raise Exception("%s undefined." % sys._getframe().f_code.co_name)

    def put(self,identifier,data=None):
        id7r = Identifier(identifier)

        if id7r.type == DATA:
            return self.put_data(id7r.name,indexer=id7r.indexer,data=data)

        raise Exception("Write is not supported for %s." % identifier)
