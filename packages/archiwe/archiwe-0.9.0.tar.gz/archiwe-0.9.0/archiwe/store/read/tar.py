#****************************************************************
# File: ./archiwe/store/read/tar.py
# (c) 2010, http://hakmatak.org, MIT License, ALL RIGHTS RESERVED
#****************************************************************
import os
from datetime import datetime

import tarfile

from hakmatak.constant import ATTRS,NODES,LEAVES
from hakmatak.constant import NAME,VALUE
from hakmatak.constant import DATA

from archive import SIZE,TYPE,MTIME
from archive import Archive

def timestamp_to_isoformat(ts):
    return datetime.fromtimestamp(ts).isoformat('T')

class StoreReader(Archive):

    # override Archive._retrieve_all_meta_from_archive()
    def _retrieve_all_meta_from_archive(self):
        #tar = tarfile.open(self.path,"r:*")
        tar = tarfile.open(self.path,"r")
        d = {}
        for tarinfo in tar:
            name = tarinfo.name
            #print name
            l = name.split('/')
            # this list must have at least 2 members
            if len(l) < 2:
                raise Exception('wrong entry in tar')
            # if a node is found
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
                    {NAME:SIZE,VALUE:tarinfo.size},
                    #{NAME:TYPE,VALUE:tarinfo.type},
                    {NAME:MTIME,VALUE:timestamp_to_isoformat(tarinfo.mtime)}
                    ]
            # if a file is found
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
                        {NAME:SIZE,VALUE:tarinfo.size},
                        #{NAME:TYPE,VALUE:tarinfo.type},
                        {NAME:MTIME,VALUE:timestamp_to_isoformat(tarinfo.mtime)}
                        ]
        tar.close()

        return d

    # override Archive._get_data_member()
    def _get_data_member(self,name):
        #tar = tarfile.open(self.path,"r:*")
        tar = tarfile.open(self.path,"r")
        fobj = tar.extractfile(name)
        bytes = fobj.read()
        fobj.close()
        tar.close()
        return bytes
