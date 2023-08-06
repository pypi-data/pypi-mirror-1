#****************************************************************
# File: ./archiwe/store/write/zip.py
# (c) 2010, http://hakmatak.org, MIT License, ALL RIGHTS RESERVED
#****************************************************************
from hakmatak.store import Writer

import zipfile

import os

class StoreWriter(Writer):

    def __init__(self,path):
        # make sure path points to a zip file if it exists
        if os.path.isfile(path) and not zipfile.is_zipfile(path):
            raise Exception("Not a zip file %s" % path)
        # superclass init
        Writer.__init__(self,path)

    def put_data(self,name,indexer=None,data=None):
        # currently no support for append/update for data slice
        if indexer not in [None,""]:
            raise Exception("put_data is not supported for indexer %s." % indexer)
        
        if data == None:
            raise Exception("Data is None.")

        zipFile = None
        if os.path.isfile(self.path):
            zipFile = zipfile.ZipFile(self.path,"a")
        else:
            zipFile = zipfile.ZipFile(self.path,"w")
        zipPath = name[1:] # strip leading '/'
        zipFile.writestr(zipPath,data)
        zipFile.close()

        return {"status":"success"}
