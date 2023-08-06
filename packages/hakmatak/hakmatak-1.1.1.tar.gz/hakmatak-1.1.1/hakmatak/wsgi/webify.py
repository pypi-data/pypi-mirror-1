#!/usr/bin/env python
#****************************************************************
# File:      ./hakmatak/wsgi/webify.py
# (c) 2010, http://hakmatak.org, MIT License, ALL RIGHTS RESERVED
#****************************************************************

from hakmatak.worker4r import Worker as ReadWorker
from hakmatak.store import ReaderClassFactory as SRCF
from hakmatak.output import WriterClassFactory as OWCF
from hakmatak.w10n import W10n

class Handler:

    def __init__(self,
        documentRoot=None,
        # for read
        readWorkerClass=ReadWorker,
        storeReaderClassFactory=SRCF(),
        outputWriterClassFactory=OWCF(),
        w10n=W10n(),
        # for write
        writeWorkerClass=None,
        storeWriterClassFactory=None,
        # whether enable write
        enableWrite=False):

        self.documentRoot = documentRoot

        self.readWorkerClass = readWorkerClass
        self.storeReaderClassFactory = storeReaderClassFactory
        self.outputWriterClassFactory = outputWriterClassFactory
        self.w10n = w10n

        self.writeWorkerClass = writeWorkerClass
        self.storeWriterClassFactory = storeWriterClassFactory

        self.enableWrite = enableWrite

    def do(self, environ, start_response):

        method = environ["REQUEST_METHOD"]

        if method in ["GET","HEAD"]:
            return self._do_read(environ, start_response)

        if method  == "PUT":
            if self.enableWrite == True:
                return self._do_write(environ, start_response)
            raise Exception("Write is not enabled for Method %s." % method)

        raise Exception("Method %s is not supported." % method)

    def _do_read(self, environ, start_response):
        from hakmatak.wsgi.webread import Handler as WebReadHandler
        handler = WebReadHandler(
            documentRoot=self.documentRoot,
            readWorkerClass=self.readWorkerClass,
            storeReaderClassFactory=self.storeReaderClassFactory,
            outputWriterClassFactory=self.outputWriterClassFactory,
            w10n=self.w10n)
        return handler.do(environ, start_response)

    def _do_write(self, environ, start_response):
        if self.writeWorkerClass == None:
            raise Exception("Write worker is null.")
        if self.storeWriterClassFactory == None:
            raise Exception("Store writer class factory is null.")
        from hakmatak.wsgi.webwrite import Handler as WebWriteHandler
        handler = WebWriteHandler(
            documentRoot=self.documentRoot,
            writeWorkerClass=self.writeWorkerClass,
            storeWriterClassFactory=self.storeWriterClassFactory)
        return handler.do(environ, start_response)

# wsgi entry point
# by default, write is NOT enabled.
def application(environ, start_response):
    return Handler().do(environ, start_response)

# cgi entry point
if __name__ == '__main__':
    import wsgiref.handlers
    wsgiref.handlers.CGIHandler().run(application)
