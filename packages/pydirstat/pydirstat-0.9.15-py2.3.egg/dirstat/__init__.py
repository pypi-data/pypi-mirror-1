#!/usr/bin/env python

# from HTMLDumper import Dumper
from SimuQT import Size
from CommandLine import CommandLine, ParseError
from Configuration import Configuration
import sys
import encodings
import imp
import os
from __version__ import __version__

def config() :
    configuration = Configuration()
    for key in configuration :
        if configuration.need_configure(key) :
            doc = configuration.get_doc(key)
            strvalue = configuration.get_strvalue(key)
            print "%s ?[%s]" % (doc,strvalue)
            line = sys.stdin.readline().replace('\r','').replace('\n','')
            if line != '' :
                configuration.set_strvalue(key,line)
    configuration.save()
    print "The file %s has been updated. Press RETURN to continue." % (configuration.get_filename(),)
    sys.stdin.readline()

def main() :
    commandline = CommandLine(sys.argv)
    e = None
    try :
    #if True :
        action = commandline.parse()
        if action == CommandLine.ACTION_DUMP :
            configuration = Configuration()
            dumpername = configuration.get_value('dumper')
            pluginpath = []
            pluginsubpath = os.path.join('dirstat','Dumpers')
            if os.path.exists(sys.argv[0]) :
                pluginpath.append(os.path.join(os.path.dirname(sys.argv[0]),pluginsubpath))
            if configuration.get_value('pluginpath') != '' :
                pluginpath.append(os.path.join(configuration.get_value('pluginpath'),pluginsubpath))
                pluginpath.append(configuration.get_value('pluginpath'))
            for pathname in sys.path :
                pluginpath.append(os.path.join(pathname,pluginsubpath))
            try :
                modulename = dumpername
                #print (modulename,pluginpath)
                moduleinfo = imp.find_module(modulename,pluginpath)
                #print (moduleinfo,)
                module = imp.load_module(modulename,*moduleinfo)
                moduleinfo[0].close()
                Dumper = module.Dumper
                Dumper().dump()
            except ImportError :
                raise ParseError('Dumper %s cannot be loaded' % (dumpername,))
        elif action == CommandLine.ACTION_USAGE :
            print commandline.get_usage(),
        elif action == CommandLine.ACTION_VERSION :
            print commandline.get_version_text(),
        elif action == CommandLine.ACTION_CONFIG :
            config()
    except (ParseError,ValueError), e :
        print commandline.get_usage()
        raise e

if __name__ == '__main__' :
    sys.argv = ['praf','--dumper=HTML',]
    main()

