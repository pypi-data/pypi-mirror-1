#!/usr/bin/env python

class FileInfoList( object ) :
    """This class store a list of FileInfo and provide iterators that sort the list as requested."""
    def __init__( self, fileInfo, param=None, bySize=False, minSize=None ) :
        self._fileInfo = fileInfo
        self._param = param
        self._bySize = bySize
        self._minSize = minSize
    def __iter__(self) :
        """Iterate on the FileInfo children, ordering them by size or not."""
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
                    if not(self._fileInfoList._minSize) or currentFileInfo.totalArea() >= self._fileInfoList._minSize :
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
                    while self._fileInfo and self._fileInfoList._minSize and self._fileInfo.totalArea() < self._fileInfoList._minSize :
                        self._fileInfo = fileInfo.next()
                    return fileInfo
                else :
                    return None

        iteratorclass = FileInfoListIteratorDefault

        if self._bySize :
            class FileInfoListIteratorBySize( FileInfoListIteratorSort ):
                def _sort(self) :
                    self._fileInfoListSorted.sort(lambda x,y:-cmp(x.totalArea(),y.totalArea()))

            iteratorclass = FileInfoListIteratorBySize

        return iteratorclass(self._fileInfo.firstChild(),self)

def test():
    pass

if __name__ == '__main__' :
    test()
