#****************************************************************
# File:      ./hakmatak/worker4r.py
# (c) 2010, http://hakmatak.org, MIT License, ALL RIGHTS RESERVED
#****************************************************************
import os

from d11n import D11n

from constant import W10N

# one way to create cache key
def create_cache_key(path,identifier,d=None):
    if d == None:
        return path+identifier
    import simplejson as json
    return path+identifier+"?"+json.dumps(d)

def special_treat(format,callback,text):
    if format != 'json' or callback == None:
        return text
    return "%s(%s)" % (callback,text)

class Worker:

    def __init__(self,
        w10nType,
        # these are user intentions
        traverse=False,
        flatten=False,
        reCache=False,
        outputFormat=None,
        callback=None,
        # this is system decision
        d11nTopDir=None,
        # for flexiblity
        storeReaderClassFactory=None,
        outputWriterClassFactory=None,
        w10n=None,
        # for caching output
        cache=None
        ):

        self.type = w10nType

        self.traverse = traverse
        self.flatten = flatten
        self.reCache = reCache
        self.outputFormat = outputFormat
        self.callback = callback

        # for decompressing file
        self.d11nTopDir = d11nTopDir
        self.enableD11n = False
        if d11nTopDir != None:
            self.enableD11n = True

        # obtain reader class
        self.readerClass = storeReaderClassFactory.create_reader_class(w10nType=self.type)

        # set writer class factory for obtaining writer class later
        self.outputWriterClassFactory = outputWriterClassFactory

        # object for dealing with w10n info
        self.w10n = w10n

        # for caching
        self.cache = cache
        self.enableCache = False
        if cache != None:
            self.enableCache = True

    def _get_params_used(self):
        return {
            'enableCache':self.enableCache,
            'traverse':self.traverse,
            'flatten':self.flatten,
            'reCache':self.reCache,
            'outputFormat':self.outputFormat,
            'callback':self.callback
            }

    def _add_extra_info(self,d):
        # ignore if w10n is None
        if self.w10n == None:
            return d
        self.w10n.type = self.type
        self.w10n.path = self.path
        self.w10n.identifier = self.identifier
        d[W10N] = self.w10n.to_list()
        return d

    # return (output,mimeType,paramsUsed)
    # note: if directory is not None, path will be relative to it.
    def get(self,path,identifier,directory=None,d11nType=None):

        if not (d11nType == None or self.enableD11n):
            raise Exception("can not decompress %s because decompression is disabled" % path)

        self.path = path
        self.identifier = identifier

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

        # the file to be webified, original or decompressed one
        thePath = path

        # cache disabled
        if not self.enableCache:
            # decompress if needed
            if not self.readerClass.canDecompress and self.enableD11n:
                d11n = D11n(self.d11nTopDir)
                thePath,isDecompressed = d11n.get(path,d11nType=d11nType)
            reader = self.readerClass(thePath)
            d,identifierType = reader.get(identifier,traverse=self.traverse,flatten=self.flatten)
            self._add_extra_info(d)
            # Writer.write() returns (output,mimeType)
            outputWriterClass = self.outputWriterClassFactory.create_writer_class(w10nType=self.type,identifierType=identifierType,format=self.outputFormat)
            output,mimeType = outputWriterClass().write(d)
            paramsUsed = self._get_params_used()
            # add more notes for debug?
            #paramsUsed['cached'] = False
            output = special_treat(self.outputFormat,self.callback,output)
            return (output,mimeType,paramsUsed)

        # cache enabled
        paramsUsedToGenerateKey = {'type':self.type,'outputFormat':self.outputFormat,'traverse':self.traverse,'flatten':self.flatten}
        key = create_cache_key(path,identifier,paramsUsedToGenerateKey)
        #print "cache key is ", key
        cached = self.cache.get(key)

        # use cache if cache found and do not have to recache
        if cached != None and not self.reCache:
            output,mimeType = cached
            paramsUsed = self._get_params_used()
            # add more notes for debug?
            #paramsUsed['cacheUsed'] = True
            output = special_treat(self.outputFormat,self.callback,output)
            return (output,mimeType,paramsUsed)

        # if cache does not exist or have to recache
        # do real work
        # decompress if needed
        if not self.readerClass.canDecompress and self.enableD11n:
            d11n = D11n(self.d11nTopDir)
            thePath,isDecompressed = d11n.get(path,d11nType=d11nType)
        reader = self.readerClass(thePath)
        d,identifierType= reader.get(identifier,traverse=self.traverse,flatten=self.flatten)
        self._add_extra_info(d)
        # Writer.write() returns (output,mimeType)
        outputWriterClass = self.outputWriterClassFactory.create_writer_class(w10nType=self.type,identifierType=identifierType,format=self.outputFormat)
        output,mimeType = outputWriterClass().write(d)
        # cache the result
        rv = self.cache.set(key,output,mimeType)
        paramsUsed = self._get_params_used()
        # add more notes for debug?
        #paramsUsed['reCached'] = True
        output = special_treat(self.outputFormat,self.callback,output)
        return (output,mimeType,paramsUsed)
