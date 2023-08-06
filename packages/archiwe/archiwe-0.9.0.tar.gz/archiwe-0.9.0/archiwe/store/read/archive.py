#****************************************************************
# File: ./archiwe/store/read/archive.py
# (c) 2010, http://hakmatak.org, MIT License, ALL RIGHTS RESERVED
#****************************************************************
import os
import sys
import md5
import cPickle as pickle

from hakmatak.constant import ATTRS,LEAVES,NODES
from hakmatak.constant import DATA
from hakmatak.constant import NAME,VALUE

from hakmatak.node import Node
from hakmatak.leaf import Leaf

from hakmatak.store import Reader

from archiwe.constant import APP_NAME

import getpass
# cache is disabled
CACHE_DIR = None
# cache is enabled
#CACHE_DIR = os.path.join("/tmp","%s-%s"%(APP_NAME,getpass.getuser()),"archive")

# attribute names common to store of archive type
SIZE = "size"
TYPE = "type"
MTIME= "mtime"

class Archive(Reader):

    # can handle compressed file internally
    # override Reader.canDecompress
    canDecompress = True

    def __init__(self,path):
        Reader.__init__(self,path)

        # all meta info of this archive file
        cacheDir = CACHE_DIR
        #cacheDir = "/tmp"
        self.meta = self._get_all_meta(cacheDir=cacheDir)
        #import simplejson as json; print json.dumps(self.meta,indent=4)

    #....................
    # initialize all meta

    def _get_all_meta(self,cacheDir=None):
        # obtain all meta for this archive file.
        # if cacheDir is None, it is retrieved directly from file itself.
        # if cacheDir is not None:
        #   if cachePath exists and is newer, it is obtained from cachePath,
        #   otherwise obtain it from archive file and have it cached too.

        meta = None

        cachePath = None
        if cacheDir != None:
            tag = md5.new(self.path).hexdigest()
            cachePath = os.path.join(cacheDir,"%s.meta.pkl" % tag)

        # try to get from cachePath
        if cachePath != None and os.path.exists(cachePath) and os.stat(cachePath).st_mtime > os.stat(self.path).st_mtime:
            f = open(cachePath,"rb")
            meta = pickle.load(f)
            f.close()
            #print >> sys.stderr, "from cache"
            return meta

        # retrieve directly from archive file if cachePath non-existent or older
        meta = self._retrieve_all_meta_from_archive()
        #print >> sys.stderr, "from archive file"

        if cachePath == None:
            return meta
        # save to cachePath
        try:
            f = open(cachePath,"wb")
            pickle.dump(meta,f,-1)
            f.close()
        except Exception, e:
            if f != None:
                f.close()
            #os.remove(cachePath)
            raise Exception("%s. Failed to cache meta. Please remove file %s manually." % (e,cachePath))
        #print >> sys.stderr, "cache it"

        return meta

    # this should be overriden by subclass
    def _retrieve_all_meta_from_archive(self):
        raise Exception("%s is not defined" % sys._getframe().f_code.co_name)

    #...............
    # deal with meta

    def _get_meta_top(self,traverse=False):
        node = Node("")

        # if traverse
        if traverse == True:
            self._rearrange_nodes_from_dict_to_list(self.meta)
            if self.meta.has_key(LEAVES):
                node.leaves = self.meta[LEAVES]
            node.nodes = self.meta[NODES]
            return node.get_meta()

        # if not traverse
        # leaves
        if self.meta.has_key(LEAVES):
            self._rearrange_leaves_from_dict_to_list(self.meta)
            node.leaves = self.meta[LEAVES]
        # sub nodes
        for name,value in self.meta[NODES].iteritems():
            if ATTRS in value.keys():
                node.nodes.append({NAME:name,ATTRS:value[ATTRS]})
            else:
                node.nodes.append({NAME:name})
        return node.get_meta()

    def _get_meta_member(self,name,traverse=False):

        d = self.meta

        a = name[1:].split("/") # skip leading '/' and split
        parents = a[:-1] # they are all dirs
        member = a[-1] # it can be dir or a file

        # go to the immediate parent of the member while sanity checking
        for x in parents:
            if not d[NODES].has_key(x):
                raise Exception("Non-existent member %s" % name)
            d = d[NODES][x]

        # if it is a node
        if d[NODES].has_key(member):
            d = d[NODES][member]
            node = Node(member)
            if d.has_key(ATTRS):
                node.attrs = d[ATTRS]
            # if traverse
            if traverse == True:
                self._rearrange_nodes_from_dict_to_list(d)
                if d.has_key(LEAVES):
                    node.leaves = d[LEAVES]
                node.nodes = d[NODES]
                return node.get_meta()
            # if not traverse
            # leaves
            if d.has_key(LEAVES):
                self._rearrange_leaves_from_dict_to_list(d)
                node.leaves = d[LEAVES]
            # nodes
            keys = d[NODES].keys(); keys.sort()
            for key in keys: 
            #for name,value in d[NODES].iteritems():
                name = key
                value = d[NODES][key]
                if value.has_key(ATTRS):
                    node.nodes.append({NAME:name,ATTRS:value[ATTRS]})
                else:
                    node.nodes.append({NAME:name})
            return node.get_meta()

        # if it is a leaf
        if d[LEAVES].has_key(member):
            d = d[LEAVES][member]
            leaf = Leaf(member)
            leaf.attrs = d[ATTRS]
            return leaf.get_meta()

        raise Exception("Non-existent member %s" % name)

    def get_meta(self,name,traverse=False):
        if name == '':
            return self._get_meta_top(traverse=traverse)
        return self._get_meta_member(name,traverse=traverse)

    #...............
    # deal with data

    # this should be overriden by subclass
    def _get_data_member(self,name):
        raise Exception("%s is not defined" % sys._getframe().f_code.co_name)

    def get_data(self,name,indexer=None,flatten=False):
        # remove leading '/' to court zip convention
        fname = name[1:]
        return {DATA:self._get_data_member(fname)}

    #.............................
    # below are supporting methods

    def _rearrange_nodes_from_dict_to_list(self,d):
        self._rearrange_leaves_from_dict_to_list(d)
        if NODES not in d:
            return
        l = []
        keys = d[NODES].keys(); keys.sort()
        for key in keys:
            value = d[NODES][key]
            # recursively go down to subnodes
            if NODES in value:
                self._rearrange_nodes_from_dict_to_list(value)
            value[NAME] = key
            l.append(value)
        # remove empty nodes
        if l == []:
            del d[NODES]
        else:
            d[NODES] = l

    def _rearrange_leaves_from_dict_to_list(self,d):
        if LEAVES not in d:
            return
        l = []
        keys = d[LEAVES].keys(); keys.sort
        for key in keys:
            value = d[LEAVES][key]
            value[NAME] = key
            l.append(value)
        # remove empty leaves
        if l == []:
            del d[LEAVES]
        else:
            d[LEAVES] = l
