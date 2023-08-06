#!/usr/bin/env python
#****************************************************************
# File:      ./hakmatak/wsgi/webread.py
# (c) 2010, http://hakmatak.org, MIT License, ALL RIGHTS RESERVED
#****************************************************************

# as required by apache
import os
#os.environ["PYTHON_EGG_CACHE"] = "/var/www/tmp/apache-python-eggs"

from cgi import parse_qs
# may use newer urlparse instead
# from urlparse import parse_qs

from hakmatak.constant import APP_NAME
import getpass

# where to store cache
# None means cache function is disabled
CACHE_TOP_DIR = None
# it must be writable by process owner, i.e.,
# wsgi daemon owner specified in wsgi.conf or
# whoever running the cgi
#CACHE_TOP_DIR = os.path.join("/tmp","%s-%s"%(APP_NAME,getpass.getuser()),"cache")

# where to store decompressed files
# None means decompression is disabled
D11N_TOP_DIR = None
# it must be writable by process owner, i.e.,
# wsgi daemon owner specified in wsgi.conf or
# whoever running the cgi
#D11N_TOP_DIR = os.path.join("/tmp","%s-%s"%(APP_NAME,getpass.getuser()),"d11n")

#........................................
# figure out parameters from query string

from hakmatak.output.factory import normalize_output_format_string

# a logical, its mere apperance will set it to True,
# regardless what the value is given in query string
def get_param_as_boolean(d,param):
    if not d.has_key(param):
        return False
    return True

def get_param_value(d,param):
    if not d.has_key(param):
        return None
    for value in d[param]:
        if value != "":
            return value
    return None

def get_params(queryString):
    # keep_blank_values = True
    d = parse_qs(queryString,True)

    params = {}

    # parameters that can take arbitrary string value
    key = "callback"
    params[key] = get_param_value(d,key)

    key = "output"
    params[key] = get_param_value(d,key)
    params[key] = normalize_output_format_string(params[key])

    # parameters that server as boolean
    for key in ["traverse","reCache","flatten"]:
        params[key] = get_param_as_boolean(d,key)

    return params

#............
# the handler

from hakmatak.worker4r import Worker
from hakmatak.store import ReaderClassFactory as SRCF
from hakmatak.output import WriterClassFactory as OWCF
from hakmatak.w10n import W10n
from hakmatak.cache import FileCache

class Handler:

    def __init__(self, documentRoot=None,
        readWorkerClass=Worker,
        storeReaderClassFactory=SRCF(),
        outputWriterClassFactory=OWCF(),
        w10n=W10n()):

        self.documentRoot = documentRoot
        self.readWorkerClass = readWorkerClass
        self.storeReaderClassFactory = storeReaderClassFactory
        self.outputWriterClassFactory = outputWriterClassFactory
        self.w10n = w10n

    def do(self, environ, start_response):

        # PATH_INFO is /type!path!indentifier as defined
        # in {cgi,wsgi}.conf by rewrite
        w10nType,path,identifier = environ['PATH_INFO'].split('!')
        w10nType = w10nType[1:] # rm leading '/'
    
        # make path absolute on server
        #path = environ['DOCUMENT_ROOT'] + path
        # use this approach instead
        # dir that the path is relative to
        docRoot = self.documentRoot
        if docRoot == None:
            docRoot = environ['DOCUMENT_ROOT']
    
        # figure out query parameters
        params = get_params(environ['QUERY_STRING'])
    
        traverse = params['traverse']
        flatten = params['flatten']
        reCache = params['reCache']
        outputFormat = params['output']
        callback = params['callback']
    
        # to cache or not
        cache = None
        if CACHE_TOP_DIR != None:
            cacheDir = os.path.join(CACHE_TOP_DIR,w10nType)
            cache = FileCache(cacheDir)
    
        # figure out if decompression
        d11nTopDir = None
        if D11N_TOP_DIR != None:
            d11nTopDir = D11N_TOP_DIR
        d11nType = None
    
        # worker goes ahead
        worker = self.readWorkerClass(
            w10nType,
            traverse=traverse,
            flatten=flatten,
            reCache=reCache,
            outputFormat=outputFormat,
            callback=callback,
            d11nTopDir=d11nTopDir,
            storeReaderClassFactory=self.storeReaderClassFactory,
            outputWriterClassFactory=self.outputWriterClassFactory,
            w10n=self.w10n,
            cache=cache
            )
        #output,mimeType,paramsUsed = worker.get(path,identifier,directory=docRoot,d11nType=d11nType)
        # d11nType is None any way.
        output,mimeType,paramsUsed = worker.get(path,identifier,directory=docRoot)
    
        # for debugging
        #import simplejson as json
        #output = json.dumps(paramsUsed,indent=4)
    
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
