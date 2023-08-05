#!/usr/bin/env python
# -*- coding : iso-8859-1 -*-

from Configuration import Configuration
from Configuration import schema
import os
from __version__ import __version__

schema_default = ['path','width','height','outputfile']

class ParseError(Exception) :
    pass

class CommandLine(object) :
    """This is the command line engine. It doesn't use parseopt because I feel like parseopt is too simple.
    Command line options should not be separated from configuration file options."""
    ACTION_NONE = 0
    ACTION_DUMP = 1
    ACTION_USAGE = 2
    ACTION_CONFIG = 3
    ACTION_VERSION = 4

    def __init__(self,commandline) :
        """Constructor. Take a command line list."""
        self._commandline = commandline
    def parse(self) :
        """Parse the command line given to constructor."""
        configuration = Configuration()

        minialiases = {}
        aliases = {}

        for key in schema :
            if 'minialias' in schema[key] :
                for letter in schema[key]['minialias'] :
                    minialiases[letter] = key
            aliases[key] = key
        rest = []
        remaining_args_to_parse = []
        next_arg_is_value = False
        next_arg_key = None
        no_name_offset = 0
        for arg in self._commandline[1:] :
            if len(remaining_args_to_parse) > 0 :
                configuration.set_strvalue(remaining_args_to_parse[0],arg)

                remaining_args_to_parse = remaining_args_to_parse[1:]
            elif arg[:2] == '--' :
                if '=' in arg :
                    (key,value) = arg[2:].split('=',1)
                else :
                    (key,value) = (arg[2:],'')
                if key in aliases :
                    if schema[aliases[key]]['needvalue'] :
                        configuration.set_strvalue(aliases[key],value)
                    else :
                        configuration.set_strvalue(aliases[key],1)
                else :
                    # error
                    raise ParseError('parameter %s does not exist' % (key,))
            elif arg[:1] == '-' :
                for letter in arg[1:] :
                    if letter in minialiases :
                        key = minialiases[letter]
                        if schema[key]['needvalue'] :
                            remaining_args_to_parse.append(key)
                        else :
                            configuration.set_strvalue(key,'1')
                    else :
                        # error
                        raise ParseError('miniparameter %s does not exist' % (letter,))
            else :
                if no_name_offset<len(schema_default) :
                    # poide
                    key = schema_default[no_name_offset]
                    if key in schema :
                        configuration.set_strvalue(key,arg)
                    else :
                        raise ParseError('parameter %s does not exist in schema' % (key,))
                        # strange error
                        pass
                else :
                    raise ParseError('need value for parameter %s' % (key,))
                    # error
                    pass

                no_name_offset += 1
        if len(remaining_args_to_parse) > 0 :
            raise ParseError('need value for parameter %s' % (remaining_args_to_parse[0],))
        if configuration.get_value('help') != 0 :
            return self.ACTION_USAGE
        if configuration.get_value('version') != 0 :
            return self.ACTION_VERSION
        if configuration.get_value('config') != 0 :
            return self.ACTION_CONFIG
        return self.ACTION_DUMP

    def get_usage(self) :
        """Return a usage string created from configuration."""
        configuration = Configuration()
        usage = '%s [OPTION]...' % (os.path.basename(self._commandline[0]),)
        for key in schema_default :
            if key in schema :
                if 'cmdlinename' in schema[key] :
                    usage += ' [%s]' % (schema[key]['cmdlinename'] ,)
                else :
                    # strange error
                    pass
            else :
                # strange error
                pass
        usage += '\n'
        usage += 'Get informations about a directory.\n'
        usage += '\n'
        usage += 'Options may be :\n'
        for key in configuration :
            if ('minialias' in schema[key]) and (schema[key]['minialias']!='') :
                minialiasstring = '-%s,' % schema[key]['minialias']
            else :
                minialiasstring = '   '
            if schema[key]['needvalue'] :
                partline = '  %s --%s=%s' % (minialiasstring,key,schema[key]['cmdlinename'])
            else :
                partline = '  %s --%s' % (minialiasstring,key,)
            partline += ' '*(30-len(partline))
            partline += '%s\n' % (schema[key]['doc']['en'],)
            usage += partline
            str
        # usage += '\n'
        return usage

    def get_version_text(self) :
        """Return a version string."""
        output = '%s %s\n' % (os.path.basename(self._commandline[0]),__version__)
        return output

def test() :
    cl = CommandLine(['poide','KUUU','-fhw','88888','45','1','7'])
    cl.parse()
    print cl.get_usage()

    configuration = Configuration()
    configuration.show()

if __name__ == '__main__' :
    test()
