#!/usr/bin/env python

import os

if not(hasattr(os,'walk')) :
    import walker
    os.walk = walker.walker

FileSizeMax = 9223372036854775807L

class FileInfo( object ):
    def __init__( self, tree=None, parent=None, name=None, statInfo=None, fileItem=None ):
        # if fileItem :
        #     # Constructor from a KFileItem, i.e. from a KIO::StatJob
        #     pass
        # elif statInfo :
        #     # Constructor from a stat buffer (i.e. based on an lstat() call).
        #     pass
        # else statInfo :
        #     # Constructor from tree/parent/name
        #     pass

        #print "Const : %s" % (( self, tree, parent, name, statInfo, fileItem ),)

        self._name         = name or ''       # the file name (without path!)
        self._isLocalFile  = True             # flag: local or remote file?
        self._device       = 0                # device this object resides on
        self._mode         = 0                # file permissions + object type
        self._links        = 0                # number of links
        self._size         = 0                # size in bytes
        self._blocks       = 0                # 512 bytes blocks
        self._mtime        = 0                # modification time

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

    def isLocalFile(self)                   : return self._isLocalFile
    def name(self)                          : return self._name

    def url(self) :
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
    def blocks(self)                        : return self._blocks
    def blockSize(self)                     : return 512
    def mtime(self)                         : return self._mtime
    def totalSize(self)                     : return self._size
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

    def locate(self, url, findDotEntries) :
        ## lname = len(self._name)
        ## if url[:lname] != self._name :
        ##     return None
        ## else :                                      # URL starts with this node's name
        ##     url = url[lname:]                       # Remove leading name of this node
        ##     if len(url) == 0 :                      # Nothing left?
        ##         return self                         # Hey! That's us!
        ##     if url[0] == "/" or url[0] == os.sep    # If the next thing a path delimiter,
        ##         url = url[1:]                       # remove that leading delimiter.
        ##     else :                                  # No path delimiter at the beginning
        ##         if self._name.[-1:] != "/" and not(self.isDotEntry()) :     # and this is not the root directory
        ##                                             # or a dot entry:
        ##             return None                     # This can't be any of our children.
        ##
        ##     child = self.firstChild()
        ##     while child :
        ##         foundChild = child.locate( url, findDotEntries );
        raise('NOT IMPLEMENTED')


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

class DirInfo( FileInfo ):
    def __init__( self, tree=None, parent=None, name=None, statInfo=None, fileItem=None, asDotEntry=False ):
        FileInfo.__init__(self, tree, parent, name, statInfo, fileItem)

        self._isDotEntry           = False  # Flag: is this entry a "dot entry"?
        self._isMountPoint         = False  # Flag: is this a mount point?
        self._pendingReadJobs      = 0      # number of open directories in this subtree

        # Children management

        self._firstChild           = None   # pointer to the first child
        self._dotEntry             = None   # pseudo entry to hold non-dir children

        # Some cached values

        self._totalSize            = self._size
        self._totalBlocks          = self._blocks
        self._totalItems           = 0
        self._totalSubDirs         = 0
        self._totalFiles           = 0
        self._latestMtime          = self._mtime

        self._summaryDirty         = False  # dirty flag for the cached values
        self._beingDestroyed       = False
        # [TODO] : Queue system
        self._readState            = None

        if asDotEntry :
            self._isDotEntry     = True
            self._dotEntry       = None
            self._name           = "."
        else :
            self._isDotEntry     = False
            # self._dotEntry       = DirInfo( tree=tree, parent=self, asDotEntry=True )

    def totalSize(self) :
        if self._summaryDirty :
            self.recalc()
        return self._totalSize

    def totalBlocks(self) :
        if self._summaryDirty :
            self.recalc()
        return self._totalBlocks

    def totalItems(self) :
        if self._summaryDirty :
            self.recalc()
        return self._totalItems

    def totalSubDirs(self) :
        if self._summaryDirty :
            self.recalc()
        return self._totalSubDirs

    def totalFiles(self) :
        if self._summaryDirty :
            self.recalc()
        return self._totalFiles

    def latestMtime(self) :
        if self._summaryDirty :
            self.recalc()
        return self._latestMtime


    def isMountPoint(self)                  : return self._isMountPoint
    def setMountPoint(self,isMountPoint) :
        self._isMountPoint = isMountPoint

    def isFinished(self) :
        return not(self.isBusy())

    def isBusy(self) :
        if self._pendingReadJobs > 0 and self._readState != 'Aborted':
            return True
        if self.readState() == 'Reading' or self.readState() == 'Queued' :
            self.readState() == 'Queued'
        return self.False

    def pendingReadJobs(self)               : return self._pendingReadJobs

    def firstChild(self)                    : return self._firstChild
    def setFirstChild(self,firstChild)      : self._firstChild = firstChild

    def insertChild(self,newChild) :
        if newChild.isDir() or (self._dotEntry == None) or self._isDotEntry :
            # print "-[%s]-[%s]-[%s]" % (self._name,newChild._name,'YES')
            # Only directories are stored directly in pure directory nodes -
            # unless something went terribly wrong, e.g. there is no dot entry to use.
            # If this is a dot entry, store everything it gets directly within it.
            #
            # In any of those cases, insert the new child in the children list.
            #
            # We don't bother with this list's order - it's explicitly declared to
            # be unordered, so be warned! We simply insert this new child at the
            # list head since this operation can be performed in constant time
            # without the need for any additional lastChild etc. pointers or -
            # even worse - seeking the correct place for insertion first. This is
            # none of our business; the corresponding "view" object for this tree
            # will take care of such niceties.
            newChild.setNext( self._firstChild )
            self._firstChild = newChild
            newChild.setParent( self )  # make sure the parent pointer is correct
            self.childAdded( newChild ) # update summaries
        else :
            # print "-[%s]-[%s]-[%s]" % (self._name,newChild._name,'NAD')
            # If the child is not a directory, don't store it directly here - use
            # this entry's dot entry instead.
            self._dotEntry.insertChild( newChild )

    def dotEntry(self)                      : return self._dotEntry
    def setDotEntry(self,dotEntry)          : self._dotEntry = dotEntry
    def isDotEntry(self)                    : return self._isDotEntry

    def childAdded(self,newChild) :
        if not(self._summaryDirty) :
            self._totalSize      += newChild.totalSize()
            self._totalBlocks    += newChild.totalBlocks()
            self._totalItems     += 1

            if newChild.isDir() :
               self._totalSubDirs+=1

            if newChild.isFile() :
                self._totalFiles+=1

            if newChild.mtime() > self._latestMtime :
                self._latestMtime = newChild.mtime()
        else :
            pass

            # Don't bother updating the summary fields if the summary is dirty
            # (i.e. outdated) anyway: As soon as anybody wants to know some exact
            # value a complete recalculation of the entire subtree will be
            # triggered. On the other hand, if nobody wants to know (which is very
            # likely) we can save this effort.

        if self._parent :
            self._parent.childAdded( newChild )

    def unlinkChild(self,deletedChild) :
        if deletedChild.parent() != self :
            return None
        if deletedChild == self._firstChild :
            self._firstChild = deletedChild.next()
            return
        child = firstChild()
        while child :
            if child.next() == deletedChild :
                child.setNext( deletedChild.next() )
                return
            child = child.next()

    def deletingChild(self,deletedChild) :
        # When children are deleted, things go downhill: Marking the summary
        # fields as dirty (i.e. outdated) is the only thing that can be done here.
        #
        # The accumulated sizes could be updated (by subtracting this deleted
        # child's values from them), but the latest mtime definitely has to be
        # recalculated: The child now being deleted might just be the one with the
        # latest mtime, and figuring out the second-latest cannot easily be
        # done. So we merely mark the summary as dirty and wait until a recalc()
        # will be triggered from outside - which might as well never happen when
        # nobody wants to know some summary field anyway.

        self._summaryDirty = True
        if self._parent :
            self._parent.deletingChild( deletedChild )

        if not(self._beingDestroyed) and (deletedChild.parent() == self) :
            # Unlink the child from the children's list - but only if this doesn't
            # happen recursively in the destructor of this object: No use
            # bothering about the validity of the children's list if this will all
            # be history anyway in a moment.
            unlinkChild( deletedChild )

    def readJobAdded(self) :
        self._pendingReadJobs+=1
        if self._parent :
            self._parent.readJobAdded()

    def readJobFinished(self) :
        self._pendingReadJobs-=1
        if self._parent :
            self._parent.readJobFinished()

    def readJobAborted(self) :
        self._readState = 'Aborted'
        if self._parent :
            self._parent.readJobAborted()

    def finalizeLocal(self) :
        self.cleanupDotEntries()

    def readState(self) :
        if self._isDotEntry and self._parent :
            return self._parent.readState()
        else :
            return self._readState

    def setReadState(self,readState) :
        if self._readState == 'Aborted' and newReadState == 'Finished' :
            return
        self._readState = newReadState

    def isDirInfo(self)                     : return True

    def recalc(self) :
        self._totalSize          = self._size
        self._totalBlocks        = self._blocks
        self._totalItems         = 0
        self._totalSubDirs       = 0
        self._totalFiles         = 0
        self._latestMtime        = self._mtime

        for fileInfo in FileInfoList(self,'AsSubDir') :
            self._totalSize      += fileInfo.totalSize()
            self._totalBlocks    += fileInfo.totalBlocks()
            self._totalItems     += fileInfo.totalItems() + 1
            self._totalSubDirs   += fileInfo.totalSubDirs()
            self._totalFiles     += fileInfo.totalFiles()

            if fileInfo.isDir() :
                self._totalSubDirs+=1

            if fileInfo.isFile() :
                self._totalFiles+=1

            childLatestMtime = fileInfo.latestMtime()

            if childLatestMtime > self._latestMtime :
                self._latestMtime = childLatestMtime

        self._summaryDirty = False

    def cleanupDotEntries(self) :
        if not(self._dotEntry) or self._isDotEntry :
            return

        # Reparent dot entry children if there are no subdirectories on this level

        if not(self._firstChild) :

            child = self._dotEntry.firstChild()

            self._firstChild = child;            # Move the entire children chain here.
            self._dotEntry.setFirstChild( 0 )    # self._dotEntry will be deleted below.

            while child :
                child.setParent( self )
                child = child.next()
        if not( self._dotEntry.firstChild() ) :
            self._dotEntry = None

class FileTree( object ) :
    def __init__(self, rootpath=None) :
        self._rootpath = rootpath
        self._root = None

    def root( self ) :
        return self._root

    def scan( self, rootpath=None ) :
        if rootpath :
            self._rootpath = rootpath
            self._root = None
        pathinfos = {}
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
                    # print "[%s] : %d v (%s)" % (subpath,pathinfos[completepath].totalSize(),completepath)
                    dirInfo.insertChild(pathinfos[completepath])
                    # print "[%s] : %d ^ (%s)" % (subpath,pathinfos[completepath].totalSize(),completepath)
                    del pathinfos[completepath]

            dirInfo.finalizeLocal()

            if path == self._rootpath :
                self._root = dirInfo
        # print "[%s]" % (pathinfos,)
        return self._root


class FileInfoList( object ) :
    def __init__( self, fileInfo, param=None, bySize=False, minSize=None ) :
        self._fileInfo = fileInfo
        self._param = param
        self._bySize = bySize
        self._minSize = minSize
    def __iter__(self) :
        class FileInfoListIterator( object ):
            def next(self) :
                fileInfo = self.next_nofail()
                if fileInfo :
                    return fileInfo
                else :
                    raise StopIteration()

        class FileInfoListIteratorSort( FileInfoListIterator ):
            def __init__(self, fileInfo, fileInfoList) :
                self._fileInfoList = fileInfoList
                currentFileInfo = fileInfo
                self._fileInfoListSorted = []
                while currentFileInfo :
                    if not(self._fileInfoList._minSize) or currentFileInfo.totalSize() >= self._fileInfoList._minSize :
                        self._fileInfoListSorted.append(currentFileInfo)
                    currentFileInfo = currentFileInfo.next()
                self._sort()
                self._index = -1
            def isValid(self) :
                return (self._index < len(self._fileInfoListSorted)) and (self._index >= 0)
            def current(self) :
                if self.isValid() :
                    return self._fileInfoListSorted[self._index]
                else :
                    return None
            def next_nofail(self) :
                self._index += 1
                return self.current()
            def next(self) :
                fileInfo = self.next_nofail()
                if fileInfo :
                    return fileInfo
                else :
                    raise StopIteration()

        class FileInfoListIteratorDefault( FileInfoListIterator ):
            def __init__(self, fileInfo, fileInfoList) :
                self._fileInfo = fileInfo
                self._fileInfoList = fileInfoList
            def isValid(self) :
                if self._fileInfo :
                    return True
                return False
            def current(self) :
                return self._fileInfo
            def next_nofail(self) :
                if self.isValid() :
                    fileInfo = self._fileInfo
                    self._fileInfo = fileInfo.next()
                    while self._fileInfo and self._fileInfoList._minSize and self._fileInfo.totalSize() < self._fileInfoList._minSize :
                        self._fileInfo = fileInfo.next()
                    return fileInfo
                else :
                    return None

        iteratorclass = FileInfoListIteratorDefault

        if self._bySize :
            class FileInfoListIteratorBySize( FileInfoListIteratorSort ):
                def _sort(self) :
                    self._fileInfoListSorted.sort(lambda x,y:-cmp(x.totalSize(),y.totalSize()))

            iteratorclass = FileInfoListIteratorBySize

        return iteratorclass(self._fileInfo.firstChild(),self)

class FileInfoListRow( object ) :
    def __init__(self) :
        self._list = []
        self._sum = 0

    def __len__(self) :
        return len(self._list)

    def first(self) :
        return self._list[0]

    def append(self,fileInfo) :
        self._sum += fileInfo.totalSize()
        return self._list.append(fileInfo)

    def sumTotalSizes(self) :
        return self._sum

    def __iter__(self):
        return iter(self._list)

def test():
    f = FileTree(rootpath='c:\\home\\gissehel').scan()
    print "(%d,%d)" % (f.totalSize(),f.size())
    print "(%d)" % (f.totalSubDirs(),)
    print "(%d)" % (f.totalItems(),)

if __name__ == '__main__' :
    test()