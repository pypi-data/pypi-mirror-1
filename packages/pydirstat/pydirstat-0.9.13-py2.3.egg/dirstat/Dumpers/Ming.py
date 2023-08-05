#!/usr/bin/env python

from dirstat.Dumper import FileDumper
from ming import *

class Dumper( FileDumper ) :
    EXT='.swf'
    NEEDHANDLE=False

    def getcolor(self, colorname):
        return colorname.get_rgb()

    def _start_dump(self) :
        size = self._tmv.visibleSize()
        self._movie = SWFMovie()

        self._movie.setDimension(self._size.x(),self._size.y())
        self._movie.setBackground(0xcc,0xcc,0xcc)
        self._movie.setRate(12)

    def _end_dump(self) :
        self._movie.save(str(self._filename))

    def addrect(self,**kwargs) :
        squareshape=SWFShape()
        squareshape.setLine(1,0,0,0)
        squareshape.setRightFill(squareshape.addFill(*self.getcolor(kwargs['color'])))
        squareshape.movePenTo(kwargs['x'],kwargs['y'])
        squareshape.drawLine(kwargs['width'],0)
        squareshape.drawLine(0,kwargs['height'])
        squareshape.drawLine(-kwargs['width'],0)
        squareshape.drawLine(0,-kwargs['height'])

        b = SWFButton()
        b.addShape(squareshape, SWFBUTTON_HIT | SWFBUTTON_UP | SWFBUTTON_DOWN | SWFBUTTON_OVER)

        filename = ""
        #filename = kwargs['filenamestr'].replace('\\','\\\\\\\\').replace('\'','\\\\\\\'') + "     " + kwargs['filesize']
        #filename = kwargs['filenamestr'].replace('\\','\\\\\\\\').replace('\'','\\\\\\\'') + "     " + kwargs['filesize']
        filename = kwargs['filenamestr'].replace('\\','\\\\\\\\').replace('\n','').replace('\'','\\\\\\\'') + "     " + kwargs['filesize']
        b.addAction(SWFAction("this.geturl('javascript:alert(\\'"+filename+"    \\')');"), SWFBUTTON_MOUSEDOWN)

        i=self._movie.add(b)
        i.moveTo(0,0)

def test():
    Dumper().dump()

if __name__ == '__main__' :
    test()
