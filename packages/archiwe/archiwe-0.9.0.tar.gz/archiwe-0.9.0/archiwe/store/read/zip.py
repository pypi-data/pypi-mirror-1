#****************************************************************
# File: ./archiwe/store/read/zip.py
# (c) 2010, http://hakmatak.org, MIT License, ALL RIGHTS RESERVED
#****************************************************************
import os
from datetime import datetime

import zipfile

from hakmatak.constant import ATTRS,NODES,LEAVES
from hakmatak.constant import NAME,VALUE
from hakmatak.constant import DATA

from archive import SIZE,TYPE,MTIME
from archive import Archive

def date_time_to_isoformat(date_time):
    # http://docs.python.org/library/zipfile.html
    # m and d are one based, H,M,S are zero based.
    y,m,d,H,M,S = date_time
    return datetime(y,m,d,H,M,S).isoformat('T')

class StoreReader(Archive):

    # override Archive._retrieve_all_meta_from_archive()
    def _retrieve_all_meta_from_archive(self):
        zip = zipfile.ZipFile(self.path,"r")
        d = {}
        for zipinfo in zip.infolist():
            name = zipinfo.filename
            # do not handle such a case now!
            if name[0] == '/':
                raise Exception("can't handle name with leading '/': %s"%name)
            # WARNING: this is our hack to make sure
            # variable 'name' is an adequate path, suitable for processing
            # by algorithm below, which counts on '/' to work properly
            if name[0:2] != './':
                name = './' + name
            #print name
            l = name.split('/')
            #print l
            # this list must have at least 2 members
            if len(l) < 2:
                raise Exception('wrong entry in zip: %s'%name)
            # a node is found
            if l[-1] == '':
                if NODES not in d:
                    d[NODES] = {}
                parent = d
                nodes = d[NODES]
                for x in l[:-1]:
                    if x not in nodes:
                        nodes[x] = {}
                    if NODES not in nodes[x]:
                        nodes[x][NODES] = {}
                    parent = nodes[x]
                    nodes = nodes[x][NODES]
                parent[ATTRS] = [
                    {NAME:SIZE,VALUE:zipinfo.file_size},
                    # in zip, there is no concept of dir?
                    #{NAME:TYPE,VALUE:zipinfo.type}, 
                    {NAME:MTIME,VALUE:date_time_to_isoformat(zipinfo.date_time)}
                    ]
            # a leaf is found
            else:
                if NODES not in d:
                    d[NODES] = {}
                parent = d
                nodes = d[NODES]
                for x in l[:-1]:
                    if x not in nodes:
                        nodes[x] = {}
                    if NODES not in nodes[x]:
                        nodes[x][NODES] = {}
                    parent = nodes[x]
                    nodes = nodes[x][NODES]
                if LEAVES not in parent:
                    parent[LEAVES] = {}
                if l[-1] not in parent[LEAVES]:
                    parent[LEAVES][l[-1]] = {}
                    parent[LEAVES][l[-1]][ATTRS] = [
                        {NAME:SIZE,VALUE:zipinfo.file_size},
                        # no type concept?
                        #{NAME:TYPE,VALUE:zipinfo.type},
                        {NAME:MTIME,VALUE:date_time_to_isoformat(zipinfo.date_time)}
                        ]
        zip.close()

        #import simplejson as json; print json.dumps(d,indent=4)

        # internal sanity checks consistent with our hack above
        if NODES not in d or ('.' not in d[NODES].keys()):
            raise Exception("internal error")

        # remove one extra level introduced by our hack above
        d = d[NODES]['.']

        #import simplejson as json; print json.dumps(d,indent=4)

        d[NAME] = ''

        # we might not need this
        #if NODES not in d:
        #    d[NODES] = []

        ## one more sanity check consistent with our hack above
        #if ATTRS in d:
        #    raise Exception("internal error")

        return d

    # override Archive._get_data_member()
    def _get_data_member(self,name):
        zip = zipfile.ZipFile(self.path,"r")
        bytes = zip.read(name)
        zip.close()
        return bytes
