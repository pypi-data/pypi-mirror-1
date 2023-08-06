#****************************************************************
# File: ./archiwe/store/write/factory.py
# (c) 2010, http://hakmatak.org, MIT License, ALL RIGHTS RESERVED
#****************************************************************
from hakmatak.store import WriterClassFactory as ParentFactory

class WriterClassFactory(ParentFactory):
    def create_writer_class(self,w10nType=None):
        if w10nType == "tar":
            from tar import StoreWriter
            return StoreWriter
        if w10nType == "zip":
            from zip import StoreWriter
            return StoreWriter
        raise Exception("Unable to create writer class for w10n type %s." % w10nType)

def main():

    writerClassFactory = WriterClassFactory()

    for w10nType in ["tar","zip"]:
        writerClass = writerClassFactory.create_writer_class(w10nType)
        print writerClass

if __name__ == "__main__":
    main()
