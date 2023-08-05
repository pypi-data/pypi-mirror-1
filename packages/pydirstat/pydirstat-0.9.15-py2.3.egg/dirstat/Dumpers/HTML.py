#!/usr/bin/env python

from dirstat.Dumper import FileDumper

HEADER='''<html>
<head>
<!-- IE stuff for security zone -->
<!-- saved from url=(0014)about:internet -->
<title>Repertoire </title>
<script language='javascript'>
<!--
function fileinfo(elm,filename,filesize) {
 document.getElementById("filename").innerHTML=filename;
 document.getElementById("filesize").innerHTML=filesize;
 // document.getElementById("tooltip").innerHTML = "<b>Nom du fichier : </b>"+filename+"<br /><b>Taille du fichier : </b>"+filesize;
 // show();
 elm._oldcolor=elm.style.backgroundColor;
 elm.style.backgroundColor="#ff0000";
}
function fileout(elm) {
 document.getElementById("filename").innerHTML="";
 document.getElementById("filesize").innerHTML="";
 // document.getElementById("tooltip").innerHTML = "";
 // hide();
 elm.style.backgroundColor=elm._oldcolor;
}
tooltipOn = false;
function show(){
  if (true){
    document.getElementById("tooltip").xwidth = document.getElementById("tooltip").offsetWidth;
    document.getElementById("tooltip").xheight = document.getElementById("tooltip").offsetHeight;
    mainwidth = 0
    mainheight = 0
    if( typeof( window.innerWidth ) == 'number' ) {
      mainwidth = window.innerWidth;
      mainheight = window.innerHeight;
    } else if( document.documentElement && ( document.documentElement.clientWidth || document.documentElement.clientHeight ) ) {
      mainwidth = document.documentElement.clientWidth;
      mainheight = document.documentElement.clientHeight;
    } else if( document.body && ( document.body.clientWidth || document.body.clientHeight ) ) {
      mainwidth = document.body.clientWidth;
      mainheight = document.body.clientHeight;
    }
    document.getElementById("tooltip").mainwidth = mainwidth
    document.getElementById("tooltip").mainheight = mainheight
    // document.getElementById("tooltip").innerHTML = "";
    tooltipOn = true;
  }
}
function hide(){
  tooltipOn = false
}
function getPosition(p){
  x = (navigator.appName.substring(0,3) == "Net") ? p.pageX : event.x+document.body.scrollLeft;
  y = (navigator.appName.substring(0,3) == "Net") ? p.pageY : event.y+document.body.scrollTop;
  if(tooltipOn){
    xleft = x-120;
    xtop = y+25;
    xwidth = document.getElementById("tooltip").xwidth;
    xheight = document.getElementById("tooltip").xheight;

    mainwidth = document.getElementById("tooltip").mainwidth
    mainheight = document.getElementById("tooltip").mainheight

    if (xleft+xwidth>mainwidth) { xleft = mainwidth-xwidth; }
    if (xleft<0) { xleft = 0; }
    if (xtop+xheight>mainheight) { xtop = mainheight-xheight; }
    if (xtop<0) { xtop = 0; }

    document.getElementById("tooltip").style.top = xtop;
    document.getElementById("tooltip").style.left = xleft;
    document.getElementById("tooltip").style.visibility = "visible";
  }
  else{
    document.getElementById("tooltip").style.visibility = "hidden";
    document.getElementById("tooltip").style.top = 0;
    document.getElementById("tooltip").style.left = 0;
  }
}
// document.onmousemove = getPosition;
document.write('<div id="tooltip" class="tooltip"></div>');
var swappanelstatus = 0;
function swappanel() {
    if (swappanelstatus==0)
    {
        document.getElementById("panelinfo").style.visibility = "hidden";
        document.getElementById("panellegend").style.visibility = "visible";
    }
    else
    {
        document.getElementById("panellegend").style.visibility = "hidden";
        document.getElementById("panelinfo").style.visibility = "visible";
    }
    swappanelstatus = 1-swappanelstatus;
}
-->
</script>
<style type='text/css'>
<!--
.tooltip {
  z-index:800;
  position:absolute;
  font-family:Verdana,Arial,Lucida,Sans-Serif;
  font-size:11px;
  border: solid 1px #808080;
  background-color:#E4E0D8;
  visibility:hidden;
  padding:1;
}
.info {
  position:absolute;
  left:5;
  top:5;
  width:%(sizex)s;
  height:30;
  font-family:Verdana,Arial,Lucida,Sans-Serif;
  font-size:11px;
  font-weight:bold;
  border: solid 1px #808080;
  background-color:#E4E0D8;
  white-space: nowrap;
  overflow: visible;
}
.rect {
  position:absolute;
  border-style:solid;
  border-width:1px;
  margin : solid 0 #fff;

  font-weight:bold;
  text-align:center;
  font-family:Verdana,Arial,Lucida,Sans-Serif;
  font-size:11px;
  white-space: nowrap;
  overflow: visible;
}
.paneltexte ,
.panel {
  position:absolute;
  left:5;
  top:40;
  width:%(sizex)s;
  height:%(sizey)s;
  background-color:none;
  border-color:#000;
  border-style:solid;
  border-width:1px;
  margin : solid 0 #fff;
}
#panelinfo {
  visibility : visible;
}
#panellegend {
  visibility : hidden;
}
#panelmetadata {
  left:5;
  top:5;
  width:%(sizexmd)s;
  height:%(sizeymd)s;

  margin : solid 1 #fff;
  margin:0;
  padding: 5px;
}
#panelmetadata p {
  font-family:Verdana,Arial,Lucida,Sans-Serif;
  font-size:11px;
}
#filename {
  padding-left: 10px;
  padding-right: 10px;
  padding-top: 2px;
  padding-bottom: 1px;
}
#filesize {
  padding-left: 10px;
  padding-right: 10px;
  padding-top: 1px;
  padding-bottom: 2px;
}
-->
</style>
</head>
<body>
<span class='info' onclick='javascript:swappanel()'>
<span id='filename'></span><br />
<span id='filesize'></span>
</span>
<span class='panel' id='panelinfo'>
'''

FOOTER_PART1='''
</span>

<span class='panel' id='panellegend'>
<span class='paneltexte' id='panelmetadata'>
'''
FOOTER_PART2='''
</span>
'''
FOOTER_PART3='''
</span>

</body>
</html>
'''

class Dumper( FileDumper ) :
    EXT='.html'

    def _start_dump(self) :
        size = self.get_size()
        self.__dump_params = {'sizex':size.x(),'sizey':size.y(),'sizexmd':size.x()/2-20,'sizeymd':size.y()-20}

        header=HEADER
        self._file.write(header % self.__dump_params)

    def _end_dump(self) :
        footer=FOOTER_PART1
        self._file.write(footer % self.__dump_params)

        params = {'Generator' : 'pydirstat','Version':'0.9.12'}
        for param in self.get_metadata() :
            self._file.write('<p><b>%s</b> : %s</p>\n' % (param[0],param[1]))

        footer=FOOTER_PART2
        self._file.write(footer % self.__dump_params)

        #--------------------------------------------------
        # legend
        #--------------------------------------------------

        types,colors,method_by_type = self.get_colors()

        border = 5
        if self.__dump_params['sizey'] < border*2*len(types)*1.3 :
            border = 0
        height=int( (self.__dump_params['sizey']-border*2.0*len(types))/len(types) )

        ypos=border
        for typename in types :
            ypos
            kwargs = {}
            kwargs['innertext'] = (typename=='_') and 'Unknown' or typename
            kwargs['x'] = int(self.__dump_params['sizex']/2+5)
            kwargs['width'] = int(self.__dump_params['sizex']/2-10)
            kwargs['y'] = ypos
            kwargs['height'] = height-2*border
            kwargs['filename'] = ''
            kwargs['filesize'] = ''
            kwargs['color'] = colors[typename]

            filelisting = []
            if typename in method_by_type :
                if 'type:extension' in method_by_type[typename] :
                    for mask in method_by_type[typename]['type:extension'] :
                        filelisting.append('*.'+mask)
                if 'type:extensionlower' in method_by_type[typename] :
                    for mask in method_by_type[typename]['type:extensionlower'] :
                        filelisting.append('*.'+mask)
                if 'type:contain' in method_by_type[typename] :
                    for mask in method_by_type[typename]['type:contain'] :
                        filelisting.append('*'+mask+'*')
                if 'type:exactmatch' in method_by_type[typename] :
                    for mask in method_by_type[typename]['type:exactmatch'] :
                        filelisting.append(mask)
            filelisting.sort()
            kwargs['filename'] = ", ".join(filelisting)
            if typename=='file' :
                if len(filelisting) > 0 :
                    kwargs['filename'] += ' and '
                kwargs['filename'] += 'any other file'
            if typename=='dir' :
                if len(filelisting) > 0 :
                    kwargs['filename'] += ' and '
                kwargs['filename'] += 'any directory'
            self.addrect(**kwargs)

            ypos += height

        #--------------------------------------------------
        # legend (end)
        #--------------------------------------------------

        footer=FOOTER_PART3
        self._file.write(footer % self.__dump_params)



    def addrect(self,**kwargs) :
        filename = kwargs['filename'].replace('\\','\\\\').replace('\'','&apos;').replace('\"','&quot;').replace('&','&amp;')
        if type(filename) != type(u'') :
            try :
                filename = filename.decode('utf8','replace')
            except LookupError :
                pass
        filename = filename.encode('iso-8859-1','replace');
        kwargs['filename'] = filename
        kwargs['colorx'] = kwargs['color'].get_htmlcolor_extended(lambda x:int(x*0.6))

        color = kwargs['color'].get_rgb()
        if color[0]+color[1]+color[2] > 3*128 :
            kwargs['colort'] = kwargs['color'].__class__(0,0,0)
        else :
            kwargs['colort'] = kwargs['color'].__class__(255,255,255)

        if 'innertext' not in kwargs :
            kwargs['innertext'] = ''
        self._file.write('''<span class='rect' onMouseOver='fileinfo(this,"%(filename)s","%(filesize)s")' onMouseOut='fileout(this)' style='left:%(x)dpx;top:%(y)dpx;width:%(width)dpx;height:%(height)dpx;background-color:%(color)s;border-color:%(colorx)s;color:%(colort)s' />%(innertext)s</span>\n''' % kwargs)

def test():
    Dumper().dump()

if __name__ == '__main__' :
    test()
