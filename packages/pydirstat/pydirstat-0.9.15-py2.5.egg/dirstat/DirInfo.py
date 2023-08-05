#!/usr/bin/env python

from FileInfo import FileInfo
from FileInfoList import FileInfoList

class DirInfo( FileInfo ):
    """This class override the FileInfo for directory"""
    def __init__( self, tree=None, parent=None, name=None, statInfo=None, asDotEntry=False ):
        FileInfo.__init__(self, tree, parent, name, statInfo)

        self._isDotEntry           = False  # Flag: is this entry a "dot entry"?
        self._isMountPoint         = False  # Flag: is this a mount point?
        self._pendingReadJobs      = 0      # number of open directories in this subtree

        # Children management

        self._firstChild           = None   # pointer to the first child
        self._dotEntry             = None   # pseudo entry to hold non-dir children

        # Some cached values

        self._totalSize            = self._size
        self._totalArea            = self._area
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
        """Return the total size of the special data used for area of tiles."""
        if self._summaryDirty :
            self.recalc()
        return self._totalSize

    def totalArea(self) :
        """Return the total area of the special data used for area of tiles."""
        if self._summaryDirty :
            self.recalc()
        return self._totalArea

    def totalBlocks(self) :
        """Return the total dir size used by block."""
        if self._summaryDirty :
            self.recalc()
        return self._totalBlocks

    def totalItems(self) :
        """Return the number of items in the directory."""
        if self._summaryDirty :
            self.recalc()
        return self._totalItems

    def totalSubDirs(self) :
        """Return the number of sub directories in the directory."""
        if self._summaryDirty :
            self.recalc()
        return self._totalSubDirs

    def totalFiles(self) :
        """Return the number of normal file in the directory."""
        if self._summaryDirty :
            self.recalc()
        return self._totalFiles

    def latestMtime(self) :
        """Return the latest modified file in the directory."""
        if self._summaryDirty :
            self.recalc()
        return self._latestMtime


    def isMountPoint(self) : return self._isMountPoint
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
        """Insert a new child in the directory."""
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
        """Called when a new child is added."""
        if not(self._summaryDirty) :
            self._totalSize      += newChild.totalSize()
            self._totalArea      += newChild.totalArea()
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
        """Remove a child from the directory."""
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
        """Remove a child from the directory."""
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
            self.unlinkChild( deletedChild )

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
        """recalc data for the directory. Used as a cache to calculate only once information if nothing changed since last call."""
        self._totalSize          = self._size
        self._totalArea          = self._area
        self._totalBlocks        = self._blocks
        self._totalItems         = 0
        self._totalSubDirs       = 0
        self._totalFiles         = 0
        self._latestMtime        = self._mtime

        for fileInfo in FileInfoList(self,'AsSubDir') :
            self._totalSize      += fileInfo.totalSize()
            self._totalArea      += fileInfo.totalArea()
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

def test():
    pass

if __name__ == '__main__' :
    test()
