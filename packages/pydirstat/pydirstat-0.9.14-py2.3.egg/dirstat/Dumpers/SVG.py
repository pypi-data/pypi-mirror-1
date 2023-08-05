#!/usr/bin/env python

from dirstat.Dumper import FileDumper

class Dumper( FileDumper ) :
    EXT='.svg'

    def _start_dump(self) :
        header='''<?xml version='1.0' encoding='iso-8859-1'?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.0//EN" "http://www.w3.org/TR/2001/REC-SVG-20010904/DTD/svg10.dtd ">
<svg width="%(sizex)dpx" viewBox="0 0 %(sizex)d %(sizey)d " height="%(sizey)dpx" xmlns="http://www.w3.org/2000/svg" >
    <script>
        var oldcolor;

        var infoTipOffsetFactor = 1;
        function hideFileAttr(evt){
            var target = evt.getTarget();
            var svgdoc = target.getOwnerDocument();
            var filenametext = svgdoc.getElementById ('filename');
            filenametext.getStyle().setProperty ('visibility', 'hidden');
            var filesizetext = svgdoc.getElementById ('filesize');
            filesizetext.getStyle().setProperty ('visibility', 'hidden');
            var svgrect = svgdoc.getElementById ('infotipRect');
            svgrect.getStyle().setProperty ('visibility', 'hidden');

            target.setAttribute('fill',oldcolor);
        }
        function setFileAttr(evt,filename,filesize){
            var target = evt.getTarget();
            var svgdoc = target.getOwnerDocument();
            var svgdocElement = svgdoc.getDocumentElement();

            var filenametext = svgdoc.getElementById ('filename');
            x = (infoTipOffsetFactor)*eval(evt.getClientX()+10);
            y = (infoTipOffsetFactor)*eval(evt.getClientY()-40);

            filenametext.getStyle().setProperty ('visibility', 'visible');
            svgobjfilename = filenametext.getFirstChild();
            svgobjfilename.setData(filename);
            var txtlen=filenametext.getComputedTextLength();

            var filesizetext = svgdoc.getElementById ('filesize');
            sx = (infoTipOffsetFactor)*eval(evt.getClientX()+10);
            sy = y+13;

            oldcolor=target.getAttribute('fill');
            target.setAttribute('fill', 'red');

            filesizetext.getStyle().setProperty ('visibility', 'visible');
            svgobjfilesize = filesizetext.getFirstChild();
            svgobjfilesize.setData(filesize);
            var sizelen=filesizetext.getComputedTextLength();


            if (y&lt;40)
            {
                y=y+100;
                sy=sy+100;
            }

            var xlen=txtlen;
            if (xlen&lt;sizelen) xlen=sizelen;

            if ((txtlen+x&gt;%(sizex)d) || (sizelen+sx&gt;%(sizex)d))
            {
                x=%(sizex)d-txtlen-10;
            }
            sx=x+xlen-sizelen;

            filenametext.setAttribute ('x', x);
            filenametext.setAttribute ('y', y);
            svgobjfilename.setData(filename);

            filesizetext.setAttribute ('x', sx);
            filesizetext.setAttribute ('y', sy);
            svgobjfilesize.setData(filesize);

            var svgrect = svgdoc.getElementById ('infotipRect');
            svgrect.getStyle().setProperty ('visibility', 'visible');
            svgrect.setAttribute ('x', x-4);
            svgrect.setAttribute ('y', y-11.5);
            svgrect.setAttribute ('width', xlen+10);
        }
    </script>
    <g style="stroke:black; stroke-width:1px">\n'''
        size = self.get_size()
        self._file.write(header % {'sizex':size.x(),'sizey':size.y()})


    def _end_dump(self) :
        footer='''
    </g>
    <g id="infotips">
    <rect id="infotipRect" x="20" y="0" width="100" height="30" rx="5" ry="5" style="visibility:hidden;fill:rgb(139,199,139);stroke-width:1; stroke:rgb(0,0,0);opacity:0.8;pointer-events:none"></rect>
    <text y="%(sizey)d" x="10" id="filename" style="visibility:visible;font-weight:normal; font-family:'Arial';font-size:13;text-anchor:left;pointer-events:none"> </text>
    <text y="%(sizey)d" x="10" id="filesize" style="visibility:hidden;fill:rgb(80,0,0);font-weight:normal; font-family:'Arial';font-size:13;text-anchor:left;pointer-events:none"> </text>
    </g>
</svg>\n'''
        size = self.get_size()
        self._file.write(footer % {'sizex':size.x(),'sizey':size.y()})

    def addrect(self,**kwargs) :
        kwargs['filename'] = kwargs['filename'].replace('\\','\\\\').replace('\'','\\\'').replace('&','&amp;').encode('iso-8859-1','replace');
        self._file.write('''        <rect x="%(x)d" y="%(y)d" height="%(height)d" width="%(width)d" onmouseover="setFileAttr(evt,'%(filename)s','%(filesize)s')" onmouseout="hideFileAttr(evt)" fill="%(color)s"/>\n''' % kwargs)

def test():
    Dumper().dump()

if __name__ == '__main__' :
    test()
