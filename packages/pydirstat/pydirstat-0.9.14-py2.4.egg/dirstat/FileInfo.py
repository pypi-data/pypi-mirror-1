#!/usr/bin/env python

import os
from SizeColorProvider import sizeColorProvider

FileSizeMax = 9223372036854775807L

class FileInfo( object ):
    """This class sotre informations about a file. Directories are stored in a child of this class : DirInfo"""
    def __init__( self, tree=None, parent=None, name=None, statInfo=None ):
        # elif statInfo :
        #     # Constructor from a stat buffer (i.e. based on an lstat() call).
        #     pass
        # else statInfo :
        #     # Constructor from tree/parent/name
        #     pass

        #print "Const : %s" % (( self, tree, parent, name, statInfo ),)

        self._name         = name or ''       # the file name (without path!)
        self._isLocalFile  = True             # flag: local or remote file?
        self._device       = 0                # device this object resides on
        self._mode         = 0                # file permissions + object type
        self._links        = 0                # number of links
        self._size         = 0                # size in bytes
        self._blocks       = 0                # 512 bytes blocks
        self._mtime        = 0                # modification time
        self._area         = 0                # area

        self._parent       = parent           # pointer to the parent entry
        self._next         = None             # pointer to the next entry
        self._tree         = tree             # pointer to the parent tree

        if statInfo :
            self._device      = statInfo.st_dev
            self._mode        = statInfo.st_mode
            self._links       = statInfo.st_nlink
            self._mtime       = statInfo.st_mtime
            if not(self.isSpecial()) :
                self._size        = statInfo.st_size
                self._blocks      = getattr(statInfo,'st_blocks',int(statInfo.st_size/512L))

        sizeColorProvider.updateFileInfo(self)
        self._area = sizeColorProvider.get_area(self)

    def isLocalFile(self)                   : return self._isLocalFile
    def name(self)                          : return self._name

    def url(self) :
        """Return url of the file (currently only support local files)"""
        if self._parent :
            parentUrl = self._parent.url()
            if self.isDotEntry() :
                return parentUrl
            if parentUrl == "/" :
                return parentUrl + self._name
            else :
                return parentUrl + os.sep + self._name
        else :
            return self._name

    def urlPart( self, targetLevel ) :
        level = self.treeLevel()
        if level < targetLevel :
            return ""

        item = self
        while level > targetLevel :
            level-=1
            item = item.parent()

        return item.name()

    def device(self)                        : return self._device
    def mode(self)                          : return self._mode
    def links(self)                         : return self._links
    def size(self)                          : return self._size
    def area(self)                          : return self._area
    def blocks(self)                        : return self._blocks
    def blockSize(self)                     : return 512
    def mtime(self)                         : return self._mtime
    def totalSize(self)                     : return self._size
    def totalArea(self)                     : return self._area
    def totalBlocks(self)                   : return self._blocks
    def totalItems(self)                    : return 0
    def totalSubDirs(self)                  : return 0
    def totalFiles(self)                    : return 0
    def latestMtime(self)                   : return self._mtime
    def isMountPoint(self)                  : return False
    def setMountPoint(self,isMountPoint)    : pass
    def isFinished(self)                    : return True
    def isBusy(self)                        : return False
    def pendingReadJobs(self)               : return 0

    def tree(self)                          : return self._tree
    def parent(self)                        : return self._parent
    def setParent(self,parent)              : self._parent = parent
    def next(self)                          : return self._next
    def setNext(self,next)                  : self._next = next

    def firstChild(self)                    : return None
    def setFirstChild(self,firstChild)      : pass




    def hasChildren(self) :
        return self.firstChild() or self.dotEntry()

    def isInSubtree(self,subtree) :
        ancestor = self
        while ancestor :
            if ancestor == subtree :
                return True
            ancestor = ancestor.parent()
        return False

    def insertChild(self)                   : pass
    def dotEntry(self)                      : return None
    def setDotEntry(self,dotEntry)          : pass
    def isDotEntry(self)                    : return False
    def treeLevel(self) :
        level   = 0
        parent  = self._parent
        while parent :
            level+=1
            parent = parent.parent()
        return level

    def childAdded(self,newChild)           : pass
    def unlinkChild(self)                   : pass
    def deletingChild(self)                 : pass
    def readState(self)                     : return 'Finished'
    def isDirInfo(self)                     : return False

    def isDir(self)                         :
        # print "-[%s]-[%s]" % (self._name,os.path.stat.S_ISDIR ( self._mode ))
        return os.path.stat.S_ISDIR ( self._mode )
    def isFile(self)                        : return os.path.stat.S_ISREG ( self._mode )
    def isSymLink(self)                     : return os.path.stat.S_ISLNK ( self._mode )
    def isDevice(self)                      : return os.path.stat.S_ISBLK ( self._mode ) or os.path.stat.S_ISCHR ( self._mode )
    def isBlockDevice(self)                 : return os.path.stat.S_ISBLK ( self._mode )
    def isCharDevice(self)                  : return os.path.stat.S_ISCHR ( self._mode )
    def isSpecial(self)                     :
        return (
            os.path.stat.S_ISBLK ( self._mode ) or
            os.path.stat.S_ISCHR ( self._mode ) or
            os.path.stat.S_ISFIFO( self._mode ) or
            os.path.stat.S_ISSOCK( self._mode )
            )

def test():
    pass

if __name__ == '__main__' :
    test()
