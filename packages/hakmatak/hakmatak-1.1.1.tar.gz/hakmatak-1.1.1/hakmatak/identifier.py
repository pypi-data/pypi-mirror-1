#****************************************************************
# File:      ./hakmatak/identifier.py
# (c) 2010, http://hakmatak.org, MIT License, ALL RIGHTS RESERVED
#****************************************************************
class IdentifierInvalidException(Exception): pass

# idenitifer types currently supported
META = "meta"
DATA = "data"

class Identifier:

    def __init__(self,idStr):
        self.type = None
        self.name = None
        self.indexer = None

        # can't be empty or None
        if idStr in ["",None]:
            raise IdentifierInvalidException("None or empty.")

        # must start with "/"
        if idStr[0] != "/":
            raise IdentifierInvalidException("No leading '/': %s."%idStr)

        # a meta identifier?
        if idStr[-1] == "/":
            self.type = META
            self.name = idStr[:-1]
            return

        # a data identifier?
        if idStr[-1] == "]":
            idx = idStr.find("[")
            # "[" and "]" are paired
            if idx == -1:
                raise IdentifierInvalidException("No pairing '[': %s."%idStr)
            self.name = idStr[:idx]
            # "[.*]" must not be proceeded with "/"
            if self.name[-1] == "/":
                raise IdentifierInvalidException("Wrong syntax: %s."%idStr)
            self.type = DATA
            self.indexer = idStr[idx+1:-1]
            return

        self.name = idStr
        return

    def get(self):
        return (self.name,self.type,self.indexer)

def test():

    idStr = "/"
    id7r = Identifier(idStr)
    assert id7r.get() == ('',META,None)

    idStr = "/this"
    id7r = Identifier(idStr)
    assert id7r.get() == ('/this',None,None)

    idStr = "/this/"
    id7r = Identifier(idStr)
    assert id7r.get() == ('/this',META,None)

    idStr = "/this[]"
    id7r = Identifier(idStr)
    assert id7r.get() == ('/this',DATA,'')

    idStr = "/this[11:22,33:66]"
    id7r = Identifier(idStr)
    assert id7r.get() == ('/this',DATA,'11:22,33:66')

    idStr = "/this/name"
    id7r = Identifier(idStr)
    assert id7r.get() == ('/this/name',None,None)

    idStr = "/this/is/a/long/name[0:10]"
    id7r = Identifier(idStr)
    assert id7r.get() == ("/this/is/a/long/name",DATA,"0:10")

    idStr = "/this/name/ has trailing space "
    id7r = Identifier(idStr)
    assert id7r.get() == ("/this/name/ has trailing space ",None,None)

    idStr = "/this/is/(virtual+variable)"
    id7r = Identifier(idStr)
    assert id7r.get() == ("/this/is/(virtual+variable)",None,None)

    idStr = "/(a*b+c*1.0-d)"
    id7r = Identifier(idStr)
    assert id7r.get() == ("/(a*b+c*1.0-d)",None,None)

    # this is for fancier indexer
    # fancier indexer uses '()'
    idStr = "/this/and/that/foo[(0,2,4,6,8),3:10,6:12]"
    id7r = Identifier(idStr)
    assert id7r.get() == ('/this/and/that/foo',DATA,'(0,2,4,6,8),3:10,6:12')
    # fancier indexer uses '[]'
    idStr = "/this/and/that/foo[[0,2,4,6,8],3:10,6:12]"
    id7r = Identifier(idStr)
    assert id7r.get() == ('/this/and/that/foo',DATA,'[0,2,4,6,8],3:10,6:12')

    print "all tests okay"

def main():

    import sys

    if (len(sys.argv) != 2):
        print "Usage: identifier"
        sys.exit(0)

    # run test()
    if sys.argv[1] == "test":
        test()
        return

    idStr, = sys.argv[1:]
    id7r = Identifier(idStr)
    print "name:",id7r.name
    print "type:",id7r.type
    print "indexer:",id7r.indexer

if __name__ == '__main__':
    main()
