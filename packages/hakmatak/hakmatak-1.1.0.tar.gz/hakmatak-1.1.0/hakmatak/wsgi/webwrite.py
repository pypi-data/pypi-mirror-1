#!/usr/bin/env python
#****************************************************************
# File:      ./hakmatak/wsgi/webwrite.py
# (c) 2010, http://hakmatak.org, MIT License, ALL RIGHTS RESERVED
#****************************************************************

# as required by apache
import os
#os.environ["PYTHON_EGG_CACHE"] = "/var/www/tmp/apache-python-eggs"

def _get_data(environ):
    if environ['REQUEST_METHOD'] != 'PUT':
        raise Exception("Wrong http method %s used for write." % environ['REQUEST_METHOD'])
    return environ['wsgi.input'].read()

from hakmatak.worker4w import Worker
from hakmatak.store import WriterClassFactory as SWCF

class Handler:

    def __init__(self,
        documentRoot=None,
        writeWorkerClass=Worker,
        storeWriterClassFactory=SWCF()):

        self.documentRoot = documentRoot
        self.writeWorkerClass = writeWorkerClass
        self.storeWriterClassFactory = storeWriterClassFactory

    def do(self, environ, start_response):

        # PATH_INFO is /type!path!indentifier as defined in wsgi.conf by rewrite
        w10nType,path,identifier = environ['PATH_INFO'].split('!')
        w10nType = w10nType[1:] # rm leading '/'
    
        # make path absolute on server
        #path = environ['DOCUMENT_ROOT'] + path
        # use this approach instead
        # dir that the path is relative to
        docRoot = self.documentRoot
        if docRoot == None:
            docRoot = environ['DOCUMENT_ROOT']
    
        # get PUT data
        data = _get_data(environ)
    
        # worker goes ahead
        worker = self.writeWorkerClass(
            w10nType,
            storeWriterClassFactory=self.storeWriterClassFactory)
        s = worker.put(path,identifier,data=data,dir=docRoot)
    
        # for debugging
        import simplejson as json
        output = json.dumps(s,indent=4)

        mimeType = "text/plain"
    
        status = '200 OK'
        response_headers = [('Content-type', mimeType),
                            ('Content-Length', str(len(output)))]
        start_response(status, response_headers)
        return [output]

# wsgi entry point
def application(environ, start_response):
    return Handler().do(environ, start_response)

# cgi entry point
if __name__ == '__main__':
    import wsgiref.handlers
    wsgiref.handlers.CGIHandler().run(application)
