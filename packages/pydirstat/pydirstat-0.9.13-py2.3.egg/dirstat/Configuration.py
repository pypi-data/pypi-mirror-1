#!/usr/bin/env python
# -*- coding : iso-8859-1 -*-

import os
import sys

CONFIGURATION_NAME = '.pydirstat.ini'

schema = {
    'width' : {
        'default' : '810',
        'type' : int,
        'minialias' : 'w',
        'doc' : {
            'en' : "Width of the graphic",
            'fr' : "Largeur du graphique en pixel",
            },
        'sortidx' : 0,
        'needvalue' : True,
        'cmdlinename' : 'WIDTH',
        },
    'height' : {
        'default' : '540',
        'type' : int,
        'minialias' : 'h',
        'doc' : {
            'en' : "Height of the graphic",
            'fr' : "Hauteur du graphique en pixel",
            },
        'sortidx' : 1,
        'needvalue' : True,
        'cmdlinename' : 'HEIGHT',
        },
    'basename' : {
        'default' : 'dirstat',
        'type' : str,
        'minialias' : 'b',
        'doc' : {
            'en' : "Basename of the final file",
            'fr' : "Base du nom du fichier final",
            },
        'sortidx' : 10,
        'needvalue' : True,
        'cmdlinename' : 'BASENAME',
        },
    'outputfile' : {
        'default' : '',
        'type' : str,
        'minialias' : 'f',
        'nosave' : True,
        'doc' : {
            'en' : "Final filename",
            'fr' : "Nom du fichier final",
            },
        'sortidx' : 100,
        'needvalue' : True,
        'cmdlinename' : 'FILE',
        },
    'path' : {
        'default' : '',
        'type' : str,
        'minialias' : 'p',
        'nosave' : True,
        'doc' : {
            'en' : "The path to analyse",
            'fr' : "Le dossier a analyser",
            },
        'sortidx' : 100,
        'needvalue' : True,
        'cmdlinename' : 'PATH',
        },
    'help' : {
        'default' : 0,
        'type' : bool,
        'minialias' : 'H',
        'nosave' : True,
        'doc' : {
            'en' : "Show help",
            'fr' : "Affiche l'aide",
            },
        'sortidx' : 999,
        'needvalue' : False,
        'cmdlinename' : 'HELP',
        },
    'version' : {
        'default' : 0,
        'type' : bool,
        'minialias' : 'v',
        'nosave' : True,
        'doc' : {
            'en' : "Show version",
            'fr' : "Affiche le numero de version",
            },
        'sortidx' : 999,
        'needvalue' : False,
        'cmdlinename' : 'VERSION',
        },
    'config' : {
        'default' : 0,
        'type' : bool,
        'minialias' : 'c',
        'nosave' : True,
        'doc' : {
            'en' : "Start configuration mode",
            'fr' : "Lance le mode configuration",
            },
        'sortidx' : 200,
        'needvalue' : False,
        'cmdlinename' : 'CFG',
        },
    'dumper' : {
        'default' : 'HTML',
        'type' : str,
        'minialias' : 'd',
        'nosave' : False,
        'doc' : {
            'en' : "Dumper used",
            'fr' : "Generateur a utiliser",
            },
        'sortidx' : 50,
        'needvalue' : True,
        'cmdlinename' : 'DUMPER',
        },
    'pluginpath' : {
        'default' : '',
        'type' : str,
        'minialias' : 'P',
        'nosave' : False,
        'doc' : {
            'en' : "Path to plugins",
            'fr' : "Chemin des plugins",
            },
        'sortidx' : 100,
        'needvalue' : True,
        'cmdlinename' : 'PPATH',
        },
    }

othersections = {
    'type:extension' : {
        "~"         : 'tmp',
        "bak"       : 'tmp',

        "c"         : 'dev',
        "cpp"       : 'dev',
        "cc"        : 'dev',
        "h"         : 'dev',
        "hpp"       : 'dev',
        "el"        : 'dev',
        "y"         : 'dev',
        "l"         : 'dev',
        "py"        : 'dev',
        "pl"        : 'dev',
        "sh"        : 'dev',

        "o"         : 'compiled',
        "lo"        : 'compiled',
        "Po"        : 'compiled',
        "al"        : 'compiled',
        "moc.cpp"   : 'compiled',
        "moc.cc"    : 'compiled',
        "elc"       : 'compiled',
        "la"        : 'compiled',
        "a"         : 'compiled',
        "rpm"       : 'compiled',
        "pyc"       : 'compiled',
        },

    'type:extensionlower' : {
        "tar.bz2"   : 'compress' ,
        "tar.gz"    : 'compress' ,
        "tgz"       : 'compress' ,
        "bz2"       : 'compress' ,
        "bz"        : 'compress' ,
        "gz"        : 'compress' ,
        "html"      : 'document' ,
        "htm"       : 'document' ,
        "txt"       : 'document' ,
        "doc"       : 'document' ,
        "png"       : 'image'    ,
        "jpg"       : 'image'    ,
        "jpeg"      : 'image'    ,
        "gif"       : 'image'    ,
        "tif"       : 'image'    ,
        "tiff"      : 'image'    ,
        "bmp"       : 'image'    ,
        "xpm"       : 'image'    ,
        "tga"       : 'image'    ,
        "svg"       : 'image'    ,
        "wav"       : 'sound'    ,
        "mp3"       : 'sound'    ,
        "avi"       : 'movie'    ,
        "mov"       : 'movie'    ,
        "mpg"       : 'movie'    ,
        "mpeg"      : 'movie'    ,
        "wmv"       : 'movie'    ,
        "asf"       : 'movie'    ,
        "ogm"       : 'movie'    ,
        "mkv"       : 'movie'    ,
        "pdf"       : 'document' ,
        "ps"        : 'image'    ,

        "exe"       : 'exec',
        "com"       : 'exec',
        "dll"       : 'lib',
        "zip"       : 'compress',
        "rar"       : 'compress',
        "arj"       : 'compress',
        "iso"       : 'compress',

        "bpk"       : 'dev',
        "tds"       : 'compiled',
        "obj"       : 'compiled',
        "bpl"       : 'lib',

        },

    'type:contain' : {
        ".so."      : 'lib',
        },

    'type:exactmatch' : {
        "core"      : 'tmp',
        },

    'color' : {
        'tmp'       : 'red',
        'dev'       : 'slateblue',
        'document'  : 'blue',
        'compiled'  : 'darkblue',
        'compress'  : 'green',
        'image'     : 'darkred',
        'sound'     : 'yellow',
        'movie'     : '#a0ff00',
        'lib'       : '#ffa0a0',
        'exec'      : 'magenta',
        'file'      : 'lightblue',
        'dir'       : 'white',
        '_'         : 'purple',
        },
    }


class _Configuration (object) :
    def __init__(self,load=True) :
        self._schema = schema
        self._strvalues = {}
        self._values = {}
        self._othersections = {}
        self._filename = None
        if load :
            self.load()

    def get_filename(self,filename=None) :
        if filename == None :
            home = os.path.expanduser('~')
            if not os.path.isdir(home) :
                # Now, we're not on unix-like environnement, nor under Win NT/2k/XP, look like Win9x !!!!
                paths_to_test = []
                if 'HOME' in os.environ :
                    paths_to_test.append(os.environ['HOME'])
                if len(sys.argv) >= 1 :
                    exe_path = os.path.split(sys.argv[0])[0]
                    if exe_path == '' :
                        exe_path = '.'
                    paths_to_test.append(exe_path)
                # We're desperate, we didn't find neither somathing looking like a "home" so we try to save config files in tmp dir !!!
                if 'TEMP' in os.environ :
                    paths_to_test.append(os.environ['TEMP'])
                # We're desperate, we didn't find neither somathing looking like a "home" so we try to save config files in tmp dir !!!
                if 'TMP' in os.environ :
                    paths_to_test.append(os.environ['TMP'])
                # As an ultimate try, we'll store this in C:\ !!! At least Win 95 have it (yes, that's Win 95 who is bothering me !)
                paths_to_test.append(os.environ['TMP'])
                for path in paths_to_test :
                    if os.path.isdir(path) :
                        home = path
                        break
            filename = os.path.join(home,CONFIGURATION_NAME)
        elif self._filename != None :
            filename = self._filename
        return filename

    def _get_value_from_strvalue(self,key,strvalue) :
        keytype = self._schema[key].get('type',str)
        functable = {
            bool : lambda x:str(x).lower() not in ('0','','False')
            }
        if keytype in functable :
            return functable[keytype](strvalue)
        return keytype(strvalue)

    def _get_strvalue_from_value(self,key,value) :
        keytype = self._schema[key].get('type',str)
        if keytype in functable :
            return functable[keytype](value)
        return "%s" % (value,)

    def load(self,filename=None) :
        filename = self.get_filename(filename)
        if os.path.isfile(filename) :
            self._filename = filename
            handle = open(filename,'rt')

            mode = ''
            for line in handle :
                line = line.replace('\r','').replace('\n','')
                if len(line)>0 and line[0] == '[' :
                    mode = ''
                    if len(line)>1 and line[-1:] == ']' :
                        mode = line[1:-1]
                elif '=' in line :
                    (key,strvalue) = line.split('=',1)
                    if mode == 'options' :
                        if key in self._schema :
                            self._strvalues[key] = strvalue
                            self._values[key] = self._get_value_from_strvalue(key,strvalue)
                    else :
                        if mode not in self._othersections :
                            self._othersections[mode] = {}
                        self._othersections[mode][key] = strvalue

        for section in othersections :
            if section not in self._othersections :
                self._othersections[section] = {}
                for key in othersections[section] :
                    self._othersections[section][key] = othersections[section][key]

    def save(self,filename=None) :
        filename = self.get_filename(filename)
        handle = open(filename,'wt')
        self._filename = filename
        handle.write("[options]\n")
        for key in self._schema :
            if ('nosave' not in self._schema[key]) or not(self._schema[key]['nosave']) :
                if key in self._strvalues :
                    handle.write("%s=%s\n" % (key,self._strvalues[key]))
                else :
                    handle.write("%s=%s\n" % (key,self._schema[key].get('default','')))
        sections = self.get_sections()
        sections.sort()
        if len(sections)>0 :
            for section in sections :
                handle.write("\n")
                handle.write("[%s]\n" % (section,))
                section_content = self.get_section(section)
                section_content_keys = section_content.keys()
                section_content_keys.sort()
                for key in section_content_keys :
                    handle.write("%s=%s\n" % (key,section_content[key]))

        handle.write("\n")
        handle.close()

    def show(self) :
        for key in self._schema :
            if key in self._strvalues :
                print "%s=%s" % (key,self._values[key])
            else :
                print "%s=%s" % (key,self._schema[key].get('default',''))

    def get_value(self,key) :
        if key in self._schema :
            if key in self._values :
                return self._values[key]
            else :
                self._strvalues[key] = self._schema[key].get('default','')
                self._values[key] = self._get_value_from_strvalue(key,self._strvalues[key])
                return self._values[key]
        else :
            return None

    def get_strvalue(self,key) :
        if key in self._schema :
            if key in self._strvalues :
                return self._strvalues[key]
            else :
                self._strvalues[key] = self._schema[key].get('default','')
                self._values[key] = self._get_value_from_strvalue(key,self._strvalues[key])
                return self._strvalues[key]
        else :
            return None

    def set_value(self,key,value) :
        if key in self._schema :
            strvalue = self._get_strvalue_from_value(key,value)
            self._strvalues[key] = strvalue
            self._values[key] = value

    def set_strvalue(self,key,strvalue) :
        if key in self._schema :
            value = self._get_value_from_strvalue(key,strvalue)
            self._strvalues[key] = strvalue
            self._values[key] = value

    def __len__(self) :
        return len(self._schema)

    def __contains__(self,key) :
        return key in self._schema

    def __iter__(self) :
        keys = self._schema.keys()
        keys.sort(lambda x,y:cmp(self._schema[x]['sortidx'],self._schema[y]['sortidx']) or cmp(x,y))
        return iter(keys)

    def get_doc(self,key,lang='en') :
        if key in self._schema :
            return self._schema[key].get('doc',{}).get(lang,'')
        return ''

    def need_configure(self,key) :
        need = True
        if ('nosave' in self._schema[key]) and self._schema[key]['nosave'] :
            need = False
        return need

    def get_sections(self) :
        return self._othersections.keys()

    def get_section(self,section) :
        if section in self._othersections :
            return self._othersections[section]
        return None

    def set_othersection_item(self,section,key,value) :
        if section not in self._othersections :
            self._othersections[section] = {}
        self._othersections[section][key] = value

class Configuration (object) :
    _borg_element = _Configuration()
    def __getattribute__(self,name) :
        return object.__getattribute__(self,'_borg_element').__getattribute__(name)
    def __iter__(self) :
        return object.__getattribute__(self,'_borg_element').__getattribute__('__iter__')()

def test() :
    c=Configuration()
    c.load()
    c.show()
    d=Configuration()

    d.set_value('width',c.get_value('width')+10)
    c.save()
    c.show()

if __name__ == '__main__' :
    test()
