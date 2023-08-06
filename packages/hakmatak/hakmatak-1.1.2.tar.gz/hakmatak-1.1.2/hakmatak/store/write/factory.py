#****************************************************************
# File:      ./hakmatak/store/write/factory.py
# (c) 2010, http://hakmatak.org, MIT License, ALL RIGHTS RESERVED
#****************************************************************
class WriterClassFactory:
    def create_writer_class(self,w10nType=None):
        raise Exception("Unable to create writer class for w10n type %s." % w10nType)

def main():

    writerClassFactory = WriterClassFactory()

    for w10nType in ["bytearray","example"]:
        writerClass = writerClassFactory.create_writer_class(w10nType)
        print writerClass

if __name__ == "__main__":
    main()
