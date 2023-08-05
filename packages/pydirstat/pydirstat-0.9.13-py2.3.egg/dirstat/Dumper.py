#!/usr/bin/env python

import os
import time
import sys
from FileInfo import FileTree
from Configuration import Configuration
from TreemapView import TreemapView
from __version__ import __version__
from SimuQT import Size,Color
from SimuQT import fmtsize

class FileDumper( object ) :
    EXT=".dump"
    NEEDHANDLE=True
    def __init__(self, rootpath=None, outputfile=None, size=None, tree=None, configuration=None) :
        self._configuration = configuration
        if self._configuration == None :
            self._configuration = Configuration()

        if rootpath == None and self._configuration.get_value('path') != '' :
            rootpath = self._configuration.get_value('path')

        # Gruik Gruik : C:" -> C:\ Thanks Windows !
        if rootpath and (len(rootpath)==3) and (rootpath[2]) == '"' :
            rootpath = rootpath[0:2] + '\\'
        if (rootpath == None) and (tree==None) :
            rootpath = '.'
        if rootpath != None :
            if os.path.supports_unicode_filenames :
                rootpath = unicode(rootpath)
            else :
                rootpath = str(rootpath)
            tree = FileTree(rootpath)
            tree.scan()

        self._rootpath = rootpath
        self._tree = tree
        filename = outputfile
        if filename == None :
            filename = self._configuration.get_value('outputfile')
        if filename == '' :
            if os.path.isdir(rootpath) :
                filename = os.path.join(rootpath,self._configuration.get_value('basename')+self.EXT)
            else :
                name = os.path.split(rootpath)[1]
                filename = name + '.' + self._configuration.get_value('basename') + self.EXT
        self._filename = filename
        self._size = size

    def dump(self,gsize=None) :
        if gsize != None :
            self._size = gsize
        if self._size == None :
            self._size = Size(self._configuration.get_value('width'),self._configuration.get_value('height'))
        self._tmv = TreemapView( self._tree, self._size, self._configuration )
        size = self._tmv.visibleSize()

        if self.NEEDHANDLE :
            self._file = file(self._filename,'wt')

        self._start_dump()
        self._tmv.draw(self)
        self._end_dump()

        if self.NEEDHANDLE :
            self._file.close()

    def get_metadata(self) :
        '''This method may be called by plugin to print metadata'''
        return [
            ('Generator', 'pydirstat'),
            ('Version', __version__),
            ('Directory', os.path.abspath(self._rootpath)),
            ('Date', time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())),
            ('Configuration File',self._configuration.get_filename()),
            ('Total Size',fmtsize(self._tmv.rootTile().orig().totalSize())),
            ('Python version',sys.version),
            ]

    def get_colors(self) :
        method_by_type = {}
        types = []
        colors = {}
        for section_name in self._configuration.get_sections() :
            if section_name.startswith('type:') :
                section_content = self._configuration.get_section(section_name)
                for key in section_content :
                    value = section_content[key]
                    if value not in method_by_type :
                        method_by_type[value] = {}
                    if section_name not in method_by_type[value] :
                        method_by_type[value][section_name] = []
                    method_by_type[value][section_name].append(key)
                    if value not in types :
                        types.append(value)
            elif section_name == 'color' :
                colors_conf = self._configuration.get_section('color')
                for color in colors_conf :
                    colors[color] = Color(colors_conf[color])

        types.sort()
        if 'file' not in types :
            types.append('file')
        if 'dir' not in types :
            types.append('dir')
        if '_' not in types :
            types.append('_')

        for typename in types :
            if typename not in colors :
                colors[typename] = colors['_']

        return types,colors,method_by_type

    def _start_dump(self) :
        '''You should override this method. Called once before starting dump.'''
        pass

    def _end_dump(self) :
        '''You should override this method. Called once after dumping all rectangle.'''
        pass

    def addrect(self,**kwargs) :
        '''You should override this method. It will be called on each rectangle. kwargs contains x,y,width,height,filename,filesize,color...'''
        pass

