#!/usr/bin/env python

"""This module simulate QT class that TreemapView needs"""

class BiXY( object ) :
    """Point and Size store quite the same content. This is the mother class for any class that store X and Y"""
    def __init__( self, x=0, y=0 ) :
        self._affect(x,y)

    def x(self, x=None) :
        if x != None :
            self._x = x
        return self._x

    def y(self, y=None) :
        if y != None :
            self._y = y
        return self._y

    def zero(self) :
        self._affect()

    def _affect(self, x=0, y=0) :
        self.x(x)
        self.y(y)

    def _copyfrom(self, fromobj) :
        self._affect(fromobj.x(),fromobj.y())

    def __str__(self):
        return "%s(%dx%d)" % (type(self).__name__,self.x(),self.y())

    def __add__(self,bi):
        return type(self)(self.x()+bi.x(),self.y()+bi.y())

class Point( BiXY ) :
    """Simulate a QPoint"""
    pass

class Size( BiXY ) :
    """Simulate a QSize"""
    pass

Size.width = Size.x
Size.height = Size.y

class Rect( Point ) :
    """Simulate a QRect"""
    def __init__( self, point=None, size=None, rect=None ) :
        if not(rect) :
            if not(point) : point=Point()
            if not(size) : size=Size()
        else :
            if not(point) : point=rect.point()
            if not(size) : size=rect.size()

        self._copyfrom(point)
        self._size = Size()
        self._size._copyfrom(size)

        self.width = self._size.width
        self.height = self._size.height
    def point(self):
        return Point(self.x(),self.y())
    def size(self):
        return Size(self.width(),self.height())
    def __str__(self):
        return "%s(%dx%d+%d+%d)" % (type(self).__name__,self.width(),self.height(),self.x(),self.y())
    def __add__(self,bi):
        return type(self)(point=self.point()+bi,size=self.size())

class Color( object ):
    """Simulate a QColor, and store color conversions. Color names can be used. They are official SVG colors. They can be used even in non-SVG dumper."""
    COLORCONV = {
            'aliceblue' : (240, 248, 255)	         ,
            'antiquewhite' : (250, 235, 215)	     ,
            'aqua' : ( 0, 255, 255)	                 ,
            'aquamarine' : (127, 255, 212)	         ,
            'azure' : (240, 255, 255)	             ,
            'beige' : (245, 245, 220)	             ,
            'bisque' : (255, 228, 196)	             ,
            'black' : ( 0, 0, 0)	                 ,
            'blanchedalmond' : (255, 235, 205)	     ,
            'blue' : ( 0, 0, 255)	                 ,
            'blueviolet' : (138, 43, 226)	         ,
            'brown' : (165, 42, 42)	                 ,
            'burlywood' : (222, 184, 135)	         ,
            'cadetblue' : ( 95, 158, 160)	         ,
            'chartreuse' : (127, 255, 0)	         ,
            'chocolate' : (210, 105, 30)	         ,
            'coral' : (255, 127, 80)	             ,
            'cornflowerblue' : (100, 149, 237)	     ,
            'cornsilk' : (255, 248, 220)	         ,
            'crimson' : (220, 20, 60)	             ,
            'cyan' : ( 0, 255, 255)	                 ,
            'darkblue' : ( 0, 0, 139)	             ,
            'darkcyan' : ( 0, 139, 139)	             ,
            'darkgoldenrod' : (184, 134, 11)	     ,
            'darkgray' : (169, 169, 169)	         ,
            'darkgreen' : ( 0, 100, 0)	             ,
            'darkgrey' : (169, 169, 169)	         ,
            'darkkhaki' : (189, 183, 107)	         ,
            'darkmagenta' : (139, 0, 139)	         ,
            'darkolivegreen' : ( 85, 107, 47)	     ,
            'darkorange' : (255, 140, 0)	         ,
            'darkorchid' : (153, 50, 204)	         ,
            'darkred' : (139, 0, 0)	                 ,
            'darksalmon' : (233, 150, 122)	         ,
            'darkseagreen' : (143, 188, 143)	     ,
            'darkslateblue' : ( 72, 61, 139)	     ,
            'darkslategray' : ( 47, 79, 79)	         ,
            'darkslategrey' : ( 47, 79, 79)	         ,
            'darkturquoise' : ( 0, 206, 209)	     ,
            'darkviolet' : (148, 0, 211)	         ,
            'deeppink' : (255, 20, 147)	             ,
            'deepskyblue' : ( 0, 191, 255)	         ,
            'dimgray' : (105, 105, 105)	             ,
            'dimgrey' : (105, 105, 105)	             ,
            'dodgerblue' : ( 30, 144, 255)	         ,
            'firebrick' : (178, 34, 34)	             ,
            'floralwhite' : (255, 250, 240)	         ,
            'forestgreen' : ( 34, 139, 34)	         ,
            'fuchsia' : (255, 0, 255)	             ,
            'gainsboro' : (220, 220, 220)	         ,
            'ghostwhite' : (248, 248, 255)	         ,
            'gold' : (255, 215, 0)	                 ,
            'goldenrod' : (218, 165, 32)	         ,
            'gray' : (128, 128, 128)	             ,
            'grey' : (128, 128, 128)	             ,
            'green' : ( 0, 128, 0)	                 ,
            'greenyellow' : (173, 255, 47)	         ,
            'honeydew' : (240, 255, 240)	         ,
            'hotpink' : (255, 105, 180)	             ,
            'indianred' : (205, 92, 92)	             ,
            'indigo' : ( 75, 0, 130)	             ,
            'ivory' : (255, 255, 240)	             ,
            'khaki' : (240, 230, 140)	             ,
            'lavender' : (230, 230, 250)	         ,
            'lavenderblush' : (255, 240, 245)	     ,
            'lawngreen' : (124, 252, 0)	             ,
            'lemonchiffon' : (255, 250, 205)	     ,
            'lightblue' : (173, 216, 230)	         ,
            'lightcoral' : (240, 128, 128)	         ,
            'lightcyan' : (224, 255, 255)	         ,
            'lightgoldenrodyellow' : (250, 250, 210),
            'lightgray' : (211, 211, 211)	         ,
            'lightgreen' : (144, 238, 144)	         ,
            'lightgrey' : (211, 211, 211)	         ,
            'lightpink' : (255, 182, 193)	         ,
            'lightsalmon' : (255, 160, 122)	         ,
            'lightseagreen' : ( 32, 178, 170)	     ,
            'lightskyblue' : (135, 206, 250)	     ,
            'lightslategray' : (119, 136, 153)	     ,
            'lightslategrey' : (119, 136, 153)	     ,
            'lightsteelblue' : (176, 196, 222)	     ,
            'lightyellow' : (255, 255, 224)	         ,
            'lime' : ( 0, 255, 0)	                 ,
            'limegreen' : ( 50, 205, 50)	         ,
            'linen' : (250, 240, 230)	             ,
            'magenta' : (255, 0, 255)	             ,
            'maroon' : (128, 0, 0)	                 ,
            'mediumaquamarine' : (102, 205, 170)	 ,
            'mediumblue' : ( 0, 0, 205)	             ,
            'mediumorchid' : (186, 85, 211)	         ,
            'mediumpurple' : (147, 112, 219)	     ,
            'mediumseagreen' : ( 60, 179, 113)	     ,
            'mediumslateblue' : (123, 104, 238)	     ,
            'mediumspringgreen' : ( 0, 250, 154)	 ,
            'mediumturquoise' : ( 72, 209, 204)	     ,
            'mediumvioletred' : (199, 21, 133)	     ,
            'midnightblue' : ( 25, 25, 112)	         ,
            'mintcream' : (245, 255, 250)	         ,
            'mistyrose' : (255, 228, 225)	         ,
            'moccasin' : (255, 228, 181)	         ,
            'navajowhite' : (255, 222, 173)	         ,
            'navy' : ( 0, 0, 128)	                 ,
            'oldlace' : (253, 245, 230)	             ,
            'olive' : (128, 128, 0)	                 ,
            'olivedrab' : (107, 142, 35)	         ,
            'orange' : (255, 165, 0)	             ,
            'orangered' : (255, 69, 0)	             ,
            'orchid' : (218, 112, 214)	             ,
            'palegoldenrod' : (238, 232, 170)	     ,
            'palegreen' : (152, 251, 152)	         ,
            'paleturquoise' : (175, 238, 238)	     ,
            'palevioletred' : (219, 112, 147)	     ,
            'papayawhip' : (255, 239, 213)	         ,
            'peachpuff' : (255, 218, 185)	         ,
            'peru' : (205, 133, 63)	                 ,
            'pink' : (255, 192, 203)	             ,
            'plum' : (221, 160, 221)	             ,
            'powderblue' : (176, 224, 230)	         ,
            'purple' : (128, 0, 128)	             ,
            'red' : (255, 0, 0)	                     ,
            'rosybrown' : (188, 143, 143)	         ,
            'royalblue' : ( 65, 105, 225)	         ,
            'saddlebrown' : (139, 69, 19)	         ,
            'salmon' : (250, 128, 114)	             ,
            'sandybrown' : (244, 164, 96)	         ,
            'seagreen' : ( 46, 139, 87)	             ,
            'seashell' : (255, 245, 238)	         ,
            'sienna' : (160, 82, 45)	             ,
            'silver' : (192, 192, 192)	             ,
            'skyblue' : (135, 206, 235)	             ,
            'slateblue' : (106, 90, 205)	         ,
            'slategray' : (112, 128, 144)	         ,
            'slategrey' : (112, 128, 144)	         ,
            'snow' : (255, 250, 250)	             ,
            'springgreen' : ( 0, 255, 127)	         ,
            'steelblue' : ( 70, 130, 180)	         ,
            'tan' : (210, 180, 140)	                 ,
            'teal' : ( 0, 128, 128)	                 ,
            'thistle' : (216, 191, 216)	             ,
            'tomato' : (255, 99, 71)	             ,
            'turquoise' : ( 64, 224, 208)	         ,
            'violet' : (238, 130, 238)	             ,
            'wheat' : (245, 222, 179)	             ,
            'white' : (255, 255, 255)	             ,
            'whitesmoke' : (245, 245, 245)	         ,
            'yellow' : (255, 255, 0)	             ,
            'yellowgreen' : (154, 205, 50)           ,
            }
    def __init__( self, arg=None, g=None, b=None ):
        if b!=None :
            (self._r, self._g, self._b) = (arg, g, b)
            self._colorname = None
        else :
            self._colorname = arg
            colors = self.COLORCONV.get(arg,None)
            if colors :
                (self._r, self._g, self._b) = colors
            else :
                colok_ok = False
                HEXDIGITS = '0123456789abcdef'
                if (self._colorname[0] == '#') and (len(self._colorname) in (4,7)) :
                    listcolor = []
                    for hexdigit in self._colorname[1:].lower() :
                        if hexdigit in HEXDIGITS :
                            listcolor.append(HEXDIGITS.index(hexdigit))
                    if len(listcolor) == 3 :
                        (self._r, self._g, self._b) = (listcolor[0]*0x11,listcolor[1]*0x11,listcolor[2]*0x11)
                        colok_ok = True
                    if len(listcolor) == 6 :
                        (self._r, self._g, self._b) = (listcolor[0]*0x10+listcolor[1],listcolor[2]*0x10+listcolor[3],listcolor[4]*0x10+listcolor[5])
                        colok_ok = True

                if not(colok_ok) :
                    (self._r, self._g, self._b) = (0x33, 0x33, 0x33)
    def get_svgcolor( self ):
        if self._colorname :
            return self._colorname
        return self.get_htmlcolor()
    def get_htmlcolor( self ):
        return '#%02x%02x%02x' % ( self._r, self._g, self._b )
    def get_htmlcolor_extended( self, func ):
        return '#%02x%02x%02x' % ( func(self._r), func(self._g), func(self._b) )
    def get_rgb( self ):
        return ( self._r, self._g, self._b )
    def __str__( self ):
        return self.get_htmlcolor()
    def __repr__( self ):
        return "Color(0x%02x,0x%02x,0x%02x)" % (self._r, self._g, self._b)

class Canvas( object ):
    """Simulate a QCanvas."""
    def __init__( self ) :
        self._size = Size()

    def size( self ) :
        return self._size

    def resize( self, width, height ) :
        self._size = Size(width, height)

def fmtsize(size) :
    """Format a number with space every 3 digits."""
    size = "%d" % (size,)
    newsize = ""
    while len(size) > 0 :
        if newsize != "" :
            newsize = " " + newsize
        newsize = size[-3:] + newsize
        size = size[:-3]
    return newsize

def test():
    r = Point(7,4)
    s = Size(100,600)
    print "r   : %s" % (r,)
    print "s   : %s" % (s,)
    print "r+s : %s" % (r+s,)
    t = Rect(point=r,size=s)

    print "t   : %s" % (t,)
    print "t+r : %s" % (t+r,)
    print "t+t : %s" % (t+t,)
    print "t+s : %s" % (t+s,)

    print Color('cyan')

if __name__ == '__main__' :
    test()
