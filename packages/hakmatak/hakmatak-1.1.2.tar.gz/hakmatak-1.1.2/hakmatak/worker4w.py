#****************************************************************
# File:      ./hakmatak/worker4w.py
# (c) 2010, http://hakmatak.org, MIT License, ALL RIGHTS RESERVED
#****************************************************************
""" For w10n write API. """

import os

class Worker:
    """Worker for write."""
    def __init__(self,
        w10nType,
        storeWriterClassFactory=None):

        self.w10nType = w10nType
        self.storeWriterClass = storeWriterClassFactory.create_writer_class(
            w10nType=w10nType)
        
    def put(self, path, identifier, data=None, directory=None):
        """ Write data for identifier in path. """

        if directory != None:
            # sanity checks on directory
            if directory[0] != "/":
                raise Exception("directory is not absolute: %s." % directory)
            if directory != os.path.normpath(directory):
                raise Exception("directory is not normalized: %s." % directory)
            # prefix path by directory
            if path[0] == '/':
                # if path is absolute, i.e., staring with '/',
                # directory is ignored by os.path.join().
                path = os.path.normpath(os.path.join(directory,path[1:]))
            else:
                path = os.path.normpath(os.path.join(directory,path))
            # sanity check on the resulting path
            if not path.startswith(directory):
                raise Exception("path %s does not start with directory %s." % directory)

        storeWriter = self.storeWriterClass(path)
        status = storeWriter.put(identifier, data=data)

        return status
