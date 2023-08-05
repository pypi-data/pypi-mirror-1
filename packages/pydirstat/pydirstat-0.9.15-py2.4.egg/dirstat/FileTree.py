#!/usr/bin/env python

from DirInfo import DirInfo
from FileInfo import FileInfo
from SizeColorProvider import sizeColorProvider
from FileProvider import FileProvider
import re

class FileTree( object ) :
    """This class scan a directory and create a tree of FileInfo."""
    def __init__(self, rootpath=None) :
        """Constructor"""

        if FileProvider.supports_unicode_filenames :
            rootpath = unicode(rootpath)
        else :
            rootpath = str(rootpath)

        self._rootpath = rootpath
        self._root = None
        self._file_provider = FileProvider(self._rootpath)
        self._exclude_list = []
        self._exclude_list_re = []

    def set_exclude_list(self,exclude_list) :
        self._exclude_list = exclude_list

    def set_exclude_list_re(self,exclude_list_re) :
        self._exclude_list_re = exclude_list_re

    def file_provider(self) :
        return self._file_provider

    def root( self ) :
        """Return the root FileInfo (usually a DirInfo)."""
        return self._root

    def rootpath( self ) :
        """Return the rootpath (a str or unicode)."""
        return self._rootpath

    def scan( self, rootpath=None ) :
        """Scan the rootpath and build the tree."""
        if rootpath :
            self._rootpath = rootpath
            self._root = None
        pathinfos = {}

        sizeColorProvider.reinitFileTree()

        exclude_list_re = []

        for exclude_item in self._exclude_list :
            exclude_list_re.append(re.compile('^'+str(exclude_item).replace('\\','\\\\').replace('.','\\.').replace('[','\\[').replace(']','\\]').replace('(','\\(').replace(')','\\)').replace('+','\\+').replace('*','.*').replace('?','.')+'$'))

        for exclude_item_re in self._exclude_list_re :
            exclude_list_re.append(re.compile(exclude_item_re))

        for infopath in self.file_provider().walk() :
            #print "[%s]" % (pathinfos,)
            (path,subpaths,files) = infopath

            if path == self._rootpath :
                name = path
            else :
                name = self.file_provider().split(path)[1]

            dirInfo = DirInfo( name=self.file_provider().get_clean_name(name), statInfo=self.file_provider().stat(path), tree=self )

            pathinfos[path] = dirInfo

            for file in files :
                exclude = False
                for exclude_item_re in exclude_list_re :
                    if exclude_item_re.match(file) :
                        exclude = True
                if not(exclude) :
                    completepath = self.file_provider().join(path,file)
                    try :
                        fileInfo = FileInfo( name=self.file_provider().get_clean_name(file), statInfo=self.file_provider().stat(completepath), tree=self, parent=dirInfo )
                        dirInfo.insertChild(fileInfo)
                    except :
                        pass

            for subpath in subpaths :
                exclude = False
                for exclude_item_re in exclude_list_re :
                    if exclude_item_re.match(subpath) :
                        exclude = True
                if not(exclude) :
                    completepath = self.file_provider().join(path,subpath)
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
