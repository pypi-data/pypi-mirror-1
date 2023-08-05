#!/usr/bin/env python

import os

from DirInfo import DirInfo
from FileInfo import FileInfo
from SizeColorProvider import sizeColorProvider

if not(hasattr(os,'walk')) :
    import walker
    os.walk = walker.walker

class FileTree( object ) :
    """This class scan a directory and create a tree of FileInfo."""
    def __init__(self, rootpath=None) :
        """Constructor"""
        self._rootpath = rootpath
        self._root = None

    def root( self ) :
        """Return the root FileInfo (usually a DirInfo)."""
        return self._root

    def scan( self, rootpath=None ) :
        """Scan the rootpath and build the tree."""
        if rootpath :
            self._rootpath = rootpath
            self._root = None
        pathinfos = {}

        sizeColorProvider.reinitFileTree()
        for infopath in os.walk(self._rootpath,False) :
            #print "[%s]" % (pathinfos,)
            (path,subpaths,files) = infopath

            if path == self._rootpath :
                name = path
            else :
                name = os.path.split(path)[1]

            dirInfo = DirInfo( name=name, statInfo=os.lstat(path), tree=self )

            pathinfos[path] = dirInfo

            for file in files :
                completepath = os.path.join(path,file)
                try :
                    fileInfo = FileInfo( name=file, statInfo=os.lstat(completepath), tree=self, parent=dirInfo )
                    dirInfo.insertChild(fileInfo)
                except :
                    pass

            for subpath in subpaths :
                completepath = os.path.join(path,subpath)
                if completepath in pathinfos :
                    # print "[%s] : %d v (%s)" % (subpath,pathinfos[completepath].totalArea(),completepath)
                    dirInfo.insertChild(pathinfos[completepath])
                    # print "[%s] : %d ^ (%s)" % (subpath,pathinfos[completepath].totalArea(),completepath)
                    del pathinfos[completepath]

            dirInfo.finalizeLocal()

            if path == self._rootpath :
                self._root = dirInfo
        # print "[%s]" % (pathinfos,)
        return self._root

def test():
    f = FileTree(rootpath='c:\\home\\gissehel').scan()
    print "(%d,%d)" % (f.totalArea(),f.area())
    print "(%d)" % (f.totalSubDirs(),)
    print "(%d)" % (f.totalItems(),)

if __name__ == '__main__' :
    test()
