#!/usr/bin/env python

from Configuration import Configuration
from SimuQT import Color
import time

class SizeColorProvider( object ) :
    def __init__(self) :
        self._configuration = Configuration()

        self._data_provider = {
            'int:size' : self.get_integer_size,
            'int:blocks' : self.get_integer_blocks,
            'int:mtime' : self.get_integer_mtime,
            'int:mtimefromnow' : self.get_integer_mtimefromnow,
            'int:one' : self.get_integer_one,
            'int:onefile' : self.get_integer_onefile,
            'type' : self.get_color_type,
            }

        self.get_color = self.get_color_type
        self.get_area = self.get_integer_size

    def reinitFileTree(self) :
        area_data_provider = self._configuration.get_value('area')
        color_data_provider = self._configuration.get_value('color')

        self._now = time.time()

        if color_data_provider[0:len('int:')]=='int:' :
            # gradient
            color_data_provider_list = color_data_provider.split(':',2)
            if len(color_data_provider_list) == 2 :
                color_data_provider_list.append('lava')
            data_provider = color_data_provider_list[0]+':'+color_data_provider_list[1]
            self._gradient_name = color_data_provider_list[2]
            gradient = self._configuration.get_section('gradient:'+self._gradient_name)
            self._gradient = map(lambda x:(float(x[0]),Color(x[1])),gradient.items())
            self._gradient.sort(lambda x,y:cmp(x[0],y[0]))

            self._max_gradient = None
            self._min_gradient = None

            self.updateFileInfo = self.updateFileInfo_gradient
            self.get_color = self.get_color_gradient
            if data_provider in self._data_provider :
                self.get_gradient = self._data_provider[data_provider]
            else :
                self.get_gradient = self.get_integer_size

        elif color_data_provider in self._data_provider :
            self.get_gradient = self._data_provider[color_data_provider]
        else :
            self.get_gradient = get_color_type

        if area_data_provider[0:len('int:')]=='int:' :
            if area_data_provider in self._data_provider :
                self.get_area = self._data_provider[area_data_provider]


    def updateFileInfo_gradient(self,fileinfo) :
        if not(fileinfo.isDir()) :
            gradient = self.get_gradient(fileinfo)
            if self._max_gradient==None or gradient>self._max_gradient :
                self._max_gradient = gradient
            if self._min_gradient==None or gradient<self._min_gradient :
                self._min_gradient = gradient

    def get_color_type(self,fileinfo) :
        """Find the Color of a file."""
        # [PyInfo] : file is a FileInfo

        tabext = self._configuration.get_section('type:extension')
        tablowerext = self._configuration.get_section('type:extensionlower')
        contain = self._configuration.get_section('type:contain')
        exactmatch = self._configuration.get_section('type:exactmatch')

        colormatch = {}
        colorconfig = self._configuration.get_section('color')
        for key in colorconfig :
            colormatch[key] = Color(colorconfig[key])

        defaultColor = colormatch.get('_',Color('purple'))

        if fileinfo :
            if fileinfo.isFile() :
                filename = fileinfo.name()
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

                # if ( ( fileinfo->mode() & S_IXUSR  ) == S_IXUSR )   return Qt::magenta;
                # if ??*isexec*?? : return colormatch.get('exec',defaultColor)

            else :
                return colormatch.get('dir',defaultColor)

        return colormatch.get('file',defaultColor)

    def get_color_gradient(self,fileinfo) :
        color = self._gradient[0][1]
        value = 1.0*(self.get_gradient(fileinfo)-self._min_gradient)/(self._max_gradient-self._min_gradient)
        for pair in self._gradient :
            if value < pair[0] :
                return color
            else :
                color = pair[1]
        return color

    def get_integer_size(self,fileinfo) :
        return fileinfo.size()

    def get_integer_blocks(self,fileinfo) :
        return fileinfo.blocks()

    def get_integer_mtime(self,fileinfo) :
        return int(fileinfo.mtime())

    def get_integer_mtimefromnow(self,fileinfo) :
        if fileinfo.isDir() :
            return 0
        return int(self._now-fileinfo.mtime())

    def get_integer_one(self,fileinfo) :
        return 1

    def get_integer_onefile(self,fileinfo) :
        if fileinfo.isDir() :
            return 0
        return 1

    def get_color(self,fileinfo) :
        """This method should not be called because get_color is overridden by another method"""

    def get_area(self,fileinfo) :
        """This method should not be called because get_area is overridden by another method"""

    def updateFileInfo(self,fileinfo) :
        """This method may or may not be called"""
        pass

sizeColorProvider = SizeColorProvider()

if __name__ == '__main__' :
    pass
