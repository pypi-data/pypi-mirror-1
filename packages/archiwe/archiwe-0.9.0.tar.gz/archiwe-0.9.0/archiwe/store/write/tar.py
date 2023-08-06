#****************************************************************
# File: ./archiwe/store/write/tar.py
# (c) 2010, http://hakmatak.org, MIT License, ALL RIGHTS RESERVED
#****************************************************************
from hakmatak.store import Writer

import tarfile
import StringIO

import os

class StoreWriter(Writer):

    def __init__(self,path):
        # make sure path points to a tar file if it exists
        if os.path.isfile(path):
            if os.path.getsize(path) == 0:
                raise Exception("File %s has zero size." % path)
            if not tarfile.is_tarfile(path):
                raise Exception("Not a tar file %s" % path)
        # superclass init
        Writer.__init__(self,path)

    def put_data(self,name,indexer=None,data=None):
        # currently no support for append/update for data slice
        if indexer not in [None,""]:
            raise Exception("put_data is not supported for indexer %s." % indexer)

        if data == None:
            raise Exception("Data is None.")

        # a member
        tarPath = name[1:] # strip leading '/'
        tarInfo = tarfile.TarInfo(name=tarPath)
        # ref: http://stackoverflow.com/questions/740820/python-write-string-directly-to-tarfile
        tarInfo.size = len(data)

        fileObj = StringIO.StringIO(data)

        tarFile = None
        if os.path.isfile(self.path):
            tarFile = tarfile.open(name=self.path,mode="a")
        else:
            tarFile = tarfile.open(name=self.path,mode="w")
        tarFile.addfile(tarInfo,fileobj=fileObj)
        tarFile.close()

        return {"status":"success"}
