#****************************************************************
# File:      ./hakmatak/store/read/factory.py
# (c) 2010, http://hakmatak.org, MIT License, ALL RIGHTS RESERVED
#****************************************************************
class ReaderClassFactory:

    def create_reader_class(self, w10nType=None):
        if w10nType == "bytearray":
            from bytearray import ByteArray
            return ByteArray
        if w10nType in ["example","example.basic"]:
            from example.basic import Basic
            return Basic
        raise Exception("Unable to create reader class for w10n type %s." % w10nType)

def main():

    readerClassFactory = ReaderClassFactory()

    for w10nType in ["bytearray","example","example.basic"]:
        readerClass = readerClassFactory.create_reader_class(w10nType)
        print readerClass

if __name__ == "__main__":
    main()
