#!/usr/bin/env python

DefaultMinTileSize          = 3
MinHeightScalePercent       = 10
MaxHeightScalePercent       = 200
DefaultHeightScalePercent   = 100
DefaultHeightScaleFactor    = ( DefaultHeightScalePercent / 100.0 )

UpdateMinSize               = 2

from FileInfo import FileInfoList, FileInfoListRow

from SimuQT import Size, Point, Rect, Color, Canvas
from SimuQT import fmtsize
import os

class TreemapView( object ):
    def __init__( self, tree, initialSize, configuration ):
        self._tree = tree
        self._rootTile = None
        self._selectedTile = None
        self._selectionRect = None
        self._tilestodraw = []
        # Not in KDirStat
        self._initialSize = initialSize
        self._configuration = configuration

        self.readConfig()

        # self.resize( initialSize )

        if tree and tree.root() :
            if not self._rootTile :
                self.rebuildTreemap( tree.root() )

    def selectedTile(self)  : return self._selectedTile
    def rootTile(self)      : return self._rootTile
    def tree(self)          : return self._tree
    def squarify(self)      : return self._squarify
    def minTileSize(self)   : return self._minTileSize

    def readConfig( self ) :
        # config =
        # self._squarify      = config.readBoolEntry( "Squarify"     , true  );
        # self._minTileSize   = config.readNumEntry ( "MinTileSize"      , DefaultMinTileSize );

        self._squarify      = True
        self._minTileSize   = DefaultMinTileSize

        # Not in KDirStat

        self._savedRootUrl  = ""

    def canvas( self ) :
        return Canvas()

    def tileAt( self, pos ) :
        tile = None

        for canvasitem in self.canvas().collisions( pos ) :
            if canvasitem :
                return canvasitem

        return None

    def _getparam_rebuildTreemap( self ) :
        root = None
        # [PyInfo] : root is a FileInfo

        if self._savedRootUrl != "" :
            root = self._tree.locate( self._savedRootUrl, true )    # node, findDotEntries

        if not root :
            if self._rootTile :
                root = _rootTile.orig()
            else :
                root = _tree.root()

        return ( root, self.canvas().size() )

    def rebuildTreemap( self, newRoot=None, newSize=None ):
        needtoclean_savedRootUrl = False
        if not newRoot :
            (newRoot,newSize) = self._getparam_rebuildTreemap()
            needtoclean_savedRootUrl = True

        if not newSize :
            newSize = self.visibleSize()

        self._selectedTile  = None;
        self._selectionRect = None;
        self._rootTile      = None;

        self.canvas().resize( newSize.width(), newSize.height() )

        if newSize.width() >= UpdateMinSize and newSize.height() >= UpdateMinSize  :
            if newRoot :
                self._rootTile = TreemapTile(
                    self,       # parentView
                    None,       # parentTile
                    newRoot,    # orig
                    Rect( point=Point(0, 0), size=newSize ),
                    'Auto' )

        # if self._tree.selection() :
        #     self.selectTile( self._tree.selection() )

        if needtoclean_savedRootUrl :
            self._savedRootUrl = ""

    def visibleSize( self ) :
        return self._initialSize

    def tileColor( self, file ) :
        # [PyInfo] : file is a FileInfo
        # [TODO] : Configuration ! I don't like hardcoded colors.

        tabext = self._configuration.get_section('type:extension')
        tablowerext = self._configuration.get_section('type:extensionlower')
        contain = self._configuration.get_section('type:contain')
        exactmatch = self._configuration.get_section('type:exactmatch')

        colormatch = {}
        colorconfig = self._configuration.get_section('color')
        for key in colorconfig :
            colormatch[key] = Color(colorconfig[key])

        defaultColor = colormatch.get('_',Color('purple'))

        if file :
            if file.isFile() :
                filename = file.name()
                idx = -1
                idx=filename.find(".",idx+1)
                while idx != -1 :
                    ext = filename[idx+1:]

                    if tabext.has_key(ext) : return colormatch.get(tabext[ext],defaultColor)
                    if tablowerext.has_key(ext.lower()) : return colormatch.get(tablowerext[ext.lower()],defaultColor)
                    idx=filename.find(".",idx+1)

                for key in contain.keys() :
                    if filename.find(key) != -1 : return colormatch.get(contain[key],defaultColor)

                for key in exactmatch.keys() :
                    if filename == key : return colormatch.get(exactmatch[key],defaultColor)

                # if ( ( file->mode() & S_IXUSR  ) == S_IXUSR )   return Qt::magenta;
                # if ??*isexec*?? : return colormatch.get('exec',defaultColor)

            else :
                return colormatch.get('dir',defaultColor)

        return colormatch.get('file',defaultColor)
    def draw(self,painter):
        for tile in self._tilestodraw :
            tile.drawShape(painter)

    def addTileToDraw(self,tile) :
        self._tilestodraw.append(tile)

class TreemapTile( object ) :
    def __init__( self, parentView, parentTile, orig, rect, orientation = 'Auto' ) :
        self._rect       = Rect(rect=rect)
        self._parentView = parentView
        self._parentTile = parentTile
        self._orig       = orig
        self._init()
        self._parentView.addTileToDraw(self)
        self.createChildren( rect, orientation )

    def rect(self) : return self._rect
    def orig(self) : return self._orig
    def parentView(self) : return self._parentView
    def parentTile(self) : return self._parentTile

    def createChildren( self, rect, orientation ) :
        if self._orig.totalSize() == 0 :
            return None

        #self.createChildrenSimple( rect, orientation )
        if self._parentView.squarify() :
            self.createSquarifiedChildren( rect )
        else :
            self.createChildrenSimple( rect, orientation )


    def createChildrenSimple( self, rect, orientation ) :
        dir      = orientation
        childDir = orientation

        if dir == 'Auto' :
            if rect.width() > rect.height() :
                dir = 'Horizontal'
            else :
                dir = 'Vertical'

        if orientation == 'Horizontal' : childDir = 'Vertical'
        if orientation == 'Vertical'   : childDir = 'Horizontal'

        offset   = 0
        size     = { 'Horizontal' : rect.width(), 'Vertical' : rect.height() }[dir]
        # count    = 0
        scale    = (1.0*size) / (1.0*self._orig.totalSize())

        fileInfoList = FileInfoList( self._orig, minSize=self._parentView.minTileSize()/scale, bySize=True, param='AsSubDir' )

        # KFileInfoSortedBySizeIterator it( _orig,
        #                               (KFileSize) ( _parentView->minTileSize() / scale ),
        #                               KDotEntryAsSubDir );


        for fileInfo in fileInfoList :
            childSize = fileInfo.totalSize()
            if childSize >= self._parentView.minTileSize() :
                if dir == 'Horizontal' :
                    childRect = Rect( point=Point(rect.x()+offset, rect.y()), size=Size(childSize, rect.height() ) )
                else :
                    childRect = Rect( point=Point(rect.x(), rect.y()+offset), size=Size(rect.width(), childSize) )

                tile = TreemapTile( self._parentView, self, fileInfo, childRect, childDir )

                offset += childSize
            # count+=1

    def createSquarifiedChildren( self, rect ) :
        if self._orig.totalSize() == 0 :
            return
        scale   = (1.0*rect.width()) * (1.0*rect.height()) / (1.0*self._orig.totalSize())
        minSize = int( self._parentView.minTileSize() / scale )

        fileInfoList = FileInfoList( self._orig, minSize=minSize, bySize=True, param='AsSubDir' )

        fileInfoListIterator = iter(fileInfoList)
        childrenRect = Rect(rect=rect)

        fileInfoListIterator.next_nofail()

        while fileInfoListIterator.isValid() :
            #fileInfoListIterator.next_nofail()
            row = self.squarify( childrenRect, scale, fileInfoListIterator )
            # print "  %s" % map(lambda x:x.name(),row._list)
            childrenRect = self.layoutRow( childrenRect, scale, row )


    def squarify( self, rect, scale, it ) :
        row = FileInfoListRow()
        fileInfo = it.current()
        # if fileInfo :
        #     print "** [%s]" % (fileInfo.name(),)

        length = max( rect.width(), rect.height() )
        if length == 0 :
            fileInfo = it.next_nofail()
            # if fileInfo :
            #     print "*- [%s]" % (fileInfo.name(),)
            return row

        improvingAspectRatio = True
        lastWorstAspectRatio = -1.0
        sum                  = 0

        # This is a bit ugly, but doing all calculations in the 'size' dimension
        # is more efficient here since that requires only one scaling before
        # doing all other calculations in the loop.
        scaledLengthSquare = length * (1.0*length) / scale

        while fileInfo and improvingAspectRatio :
            sum += fileInfo.totalSize()
            if (len(row)!=0) and (sum != 0) and (fileInfo.totalSize() != 0) :
                sumSquare        = sum * sum
                worstAspectRatio = max( scaledLengthSquare * row.first().totalSize() / sumSquare,
                                        sumSquare / ( scaledLengthSquare * fileInfo.totalSize() ) )

                if (lastWorstAspectRatio >= 0.0) and (worstAspectRatio > lastWorstAspectRatio) :
                    improvingAspectRatio = False

                lastWorstAspectRatio = worstAspectRatio

            if improvingAspectRatio :
                row.append( fileInfo )
                fileInfo = it.next_nofail()
                # if fileInfo :
                #     print "*+ [%s]" % (fileInfo.name(),)

        return row

    def layoutRow( self, rect, scale, row ):
        # [TODO]
        if len(row) == 0 :
            return rect

        if rect.width() > rect.height() :
            dir = 'Horizontal'
        else :
            dir = 'Vertical'

        primary = max( rect.width(), rect.height() )

        sum = row.sumTotalSizes()
        secondary = int( sum * (1.0*scale) / primary )

        if sum == 0 : # Prevent division by zero.
            return rect

        if secondary < self._parentView.minTileSize() : # We don't want tiles that small.
            return rect

        offset = 0
        remaining = primary

        for fileInfo in row :
            childSize = int( (1.0*fileInfo.totalSize()) / (1.0* sum) * primary + 0.5 )
            if childSize > remaining : # Prevent overflow because of accumulated rounding errors
                childSize = remaining

            remaining -= childSize


            if childSize >= self._parentView.minTileSize() :
                if dir == 'Horizontal' :
                    childRect = Rect( Point(rect.x()+offset, rect.y()), Size(childSize, secondary) )
                else :
                    childRect = Rect( Point(rect.x(), rect.y()+offset), Size(secondary, childSize) )

                tile = TreemapTile( self._parentView, self, fileInfo, childRect, orientation='Auto' )
                # What should I do with the tile ?
                offset += childSize

        if ( dir == 'Horizontal' ) :
            newRect = Rect( Point(rect.x(), rect.y()+secondary), Size(rect.width(), rect.height()-secondary) )
        else :
            newRect = Rect( Point(rect.x()+secondary, rect.y()), Size(rect.width()-secondary, rect.height()) )

        return newRect

    def drawShape( self, painter ):
        size = self.rect().size()

        #print "drawShape(%s) [%s] <%s>" % (self.rect(),self._orig.name(),self._parentView.tileColor( self._orig ))

        if size.height() < 1 or size.width() < 1 :
            return

        def iconv(name) :
            result = ""
            for letter in name :
                if ord(letter) < 255 :
                    result += chr(ord(letter))
                else :
                    result += "."
            return result

        painter.addrect(
            x=self.rect().x(),
            y=self.rect().y(),
            width=self.rect().width(),
            height=self.rect().height(),
            color=self._parentView.tileColor( self._orig ),
            filename=self._orig.url(),
            #filenamestr=str(self._orig.url().encode('iso-8859-1','replace')),
            #filenamestr=str(iconv(self._orig.url())),
            #filenamestr=iconv(self._orig.url()),
            filenamestr=iconv(self._orig.url()),
            filesize=fmtsize(self._orig.totalSize())
            )

        # painter.setPen( Pen( self._parentView.outlineColor(), 1 ) )
        # if self._orig.isDir() and self._orig.isDotEntry() :
        #     painter.setBrush( self._parentView.dirFillColor() )
        # else :
        #     painter.setBrush( self._parentView.tileColor( self._orig ) )

        # [TODO] : Draw what need to be drawn

    def _init( self ):
        # [TODO] : find if I need to use Z order
        # setZ( _parentTile ? ( _parentTile->z() + 1.0 ) : 0.0 );
        # setBrush( QColor( 0x60, 0x60, 0x60 ) );
        # setPen( NoPen );
        pass

if __name__ == '__main__' :
    pass



