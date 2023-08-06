#****************************************************************
# File: ./archiwe/store/read/factory.py
# (c) 2010, http://hakmatak.org, MIT License, ALL RIGHTS RESERVED
#****************************************************************
from hakmatak.store import ReaderClassFactory as ParentFactory

class ReaderClassFactory(ParentFactory):

    def create_reader_class(self,w10nType=None):
        if w10nType == "tar":
            from tar import StoreReader
            return StoreReader
        if w10nType == "zip":
            from zip import StoreReader
            return StoreReader
        raise Exception("Unable to create reader class for w10n type %s." % w10nType)
        #return ParentFactory.create_reader_class(self,w10nType=w10nType)

def main():

    readerClassFactory = ReaderClassFactory()

    for w10nType in ["tar","zip"]:
        readerClass = readerClassFactory.create_reader_class(w10nType)
        print readerClass

if __name__ == "__main__":
    main()
