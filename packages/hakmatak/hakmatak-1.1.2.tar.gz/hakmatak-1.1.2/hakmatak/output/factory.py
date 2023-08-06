#****************************************************************
# File:      ./hakmatak/output/factory.py
# (c) 2010, http://hakmatak.org, MIT License, ALL RIGHTS RESERVED
#****************************************************************
from hakmatak.identifier import META,DATA

# convert to canonical format string
# should be consistent with class WriterClassFactory below
def normalize_output_format_string(format):
    if format == None:
        return None
    format = format.lower()
    if format in ['htm','html']:
        return 'html'
    if format in ['big-endian','bigendian','be']:
        return 'be'
    if format in ['little-endian','littleendian','le']:
        return 'le'
    if format in ['nc','netcdf']:
        return 'nc'
    return format

class WriterClassFactory:

    """ identifierType: can only be "meta" or "data" for now
        format: output format
    """
    def create_writer_class(self,w10nType=None,identifierType=None,format=None):
        if identifierType == META:
            return self.create_writer_class_meta(format=format)
        if identifierType == DATA:
            return self.create_writer_class_data(format=format)
        raise Exception("Unable to create writer for identifierType %s." % identifierType)

    def create_writer_class_meta(self,format=None):
        # default to json if it is meta
        if format == None:
            format = "json"

        if format == "json":
            from json import Json
            return Json

        if format == "html":
            from html.dirlist import DirList
            return DirList

        raise Exception("Format %s is not supported for meta." % format)

    def create_writer_class_data(self,format=None):
        # default to raw
        if format == None:
            format = "raw"

        if format == "raw":
            from raw import Raw
            return Raw

        if format == "json":
            from json import Json
            return Json

        raise Exception("Format %s is not supported for data." % format)

def main():

    writerClassFactory = WriterClassFactory()

    identifierType = META; format = "json"
    writerClass = writerClassFactory.create_writer_class(identifierType=identifierType,format=format)
    print writerClass

    identifierType = META; format = "html"
    writerClass = writerClassFactory.create_writer_class(identifierType=identifierType,format=format)
    print writerClass

    identifierType = DATA; format = "json"
    writerClass = writerClassFactory.create_writer_class(identifierType=identifierType,format=format)
    print writerClass

    identifierType = DATA; format = "html"
    writerClass = writerClassFactory.create_writer_class(identifierType=identifierType,format=format)
    print writerClass

if __name__ == "__main__":
    main()
