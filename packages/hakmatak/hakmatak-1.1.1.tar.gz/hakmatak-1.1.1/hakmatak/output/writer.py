#****************************************************************
# File:      ./hakmatak/output/writer.py
# (c) 2010, http://hakmatak.org, MIT License, ALL RIGHTS RESERVED
#****************************************************************
import sys

class Writer:

    # must be overriden
    # d: a python dictionary that mirrors w10n JSON response
    # return (str,mimeType)
    def write(self,d,path=None):
        raise Exception("%s undefined" % sys._getframe().f_code.co_name)
