"""
NAME:
    setup.py

SYNOPSIS:
    python setup.py [options] [command]

DESCRIPTION:
    Using distutils "setup", build, install, or make tarball of the package.

OPTIONS:
    See Distutils documentation for details on options and commands.
    Common commands:
    build               build the package, in preparation for install
    install             install module(s)/package(s) [runs build if needed]
    install_data        install datafiles (e.g., in a share dir)
    install_scripts     install executable scripts (e.g., in a bin dir)
    sdist               make a source distribution
    bdist               make a binary distribution
    clean               remove build temporaries

EXAMPLES:
    cd mydir
    (cp myfile-0.1.tar.gz here)
    gzip -cd myfile-0.1.tar.gz | tar xvf -
    cd myfile-0.1
    python setup.py build
    python setup.py install
    python setup.py sdist
"""

#===imports=============
import os
import sys
#import re
import string
import getopt
#import shutil
#import commands
#===setuptools======
import ez_setup # From http://peak.telecommunity.com/DevCenter/setuptools
ez_setup.use_setuptools()

from setuptools import setup, find_packages, Extension

#===patch2.2.3======
# patch distutils if it can't cope with the "classifiers" or
# "download_url" keywords
if sys.version < '2.2.3':
    from distutils.dist import DistributionMetadata
    DistributionMetadata.classifiers = None
    DistributionMetadata.download_url = None

#===globals======
modname='setup'
debug_p=0

#===configuration======
pkgname='pydirstat'
version=string.strip(open("VERSION").readline())
exec_prefix=sys.exec_prefix
description = "Show statistics informations for a directory in HTML, SVG, or Flash."
long_description = """pyDirStat is a small tool to view statistical information
about a directory. It will generate a view of all files contained in a
directory (and subdirectories) with rectangles. Each rectangle area is
proportional to file size.
It's a perfect tool to view disk usage with graphics."""
author = "Arthibus Gissehel"
author_email = "public-pds-setup@giss.ath.cx"
url="http://pydirstat.berlios.de/"
classifiers=[
    'Development Status :: 4 - Beta',
    'Environment :: Console',
    'Environment :: Web Environment',
    'Environment :: Win32 (MS Windows)',
    'Intended Audience :: End Users/Desktop',
    'Intended Audience :: System Administrators',
    'License :: OSI Approved :: GNU General Public License (GPL)',
    'Operating System :: Microsoft :: Windows',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: System :: Filesystems',
    'Topic :: System :: Systems Administration',
    ]
#download_url='http://developer.berlios.de/project/showfiles.php?group_id=3108'

scripts=[
    'src/pds-config.py',
    'src/pdshtml.py',
    'src/pdssvg.py',
    'src/pdsswf.py',
    'src/pydirstat.py',
    ]
py_modules=[]
packages=[
    'dirstat',
    'dirstat/Dumpers',
    ]
package_dir = {'': 'src'}
package_data = {
    '': 'src',
    }
ext_modules=[]
#   [Extension('my_ext', ['my_ext.c', 'file1.c', 'file2.c'],
#           include_dirs=[''],
#           library_dirs=[''],
#           libraries=[''],)
#    ]
zip_safe = False
options={}
extra_parameters = {}
#===py2exe==========================
try :
    import py2exe
    extra_parameters['console'] = [
        {
            'icon_resources':[(0,'res/pydirstat.ico')],
            'script':'src/pydirstat.py',
            },
        {
            'icon_resources':[(0,'res/pydirstat.ico')],
            'script':'src/pds-config.py',
            },
        ]
    options["py2exe"] = {
        "includes" : [
            'encodings',
            'encodings.latin_1',
            'dirstat.Dumpers.HTML',
            'dirstat.Dumpers.SVG',
            'dirstat.Dumpers.Ming',
            ],
        "excludes": [],
        }
except ImportError :
    pass
#===utilities==========================
def debug(ftn,txt):
    if debug_p:
        sys.stdout.write("%s.%s:%s\n" % (modname,ftn,txt))
        sys.stdout.flush()

def fatal(ftn,txt):
    msg="%s.%s:FATAL:%s\n" % (modname,ftn,txt)
    raise SystemExit, msg

def usage():
    print __doc__

#=============================
def main():
    setup (#---meta-data---
           name = pkgname,
           version = version,
           description = description,
           long_description = long_description,
           author = author,
           author_email = author_email,
           url=url,
           classifiers = classifiers,
           #download_url=download_url,

           #---scripts,modules and packages---
           scripts=scripts,
           py_modules = py_modules,
           package_dir = package_dir,
           packages = packages,
           ext_modules = ext_modules,

           #---egg params---
           zip_safe = zip_safe,

           #---other---
           options = options,
           **extra_parameters
           )
#==============================
if __name__ == '__main__':
    opts,pargs=getopt.getopt(sys.argv[1:],'hv',
                 ['help','version','exec-prefix'])
    for opt in opts:
        if opt[0]=='-h' or opt[0]=='--help':
            usage()
            sys.exit(0)
        elif opt[0]=='-v' or opt[0]=='--version':
            print modname+": version="+version
        elif opt[0]=='--exec-prefix':
            exec_prefix=opt[1]

    for arg in pargs:
        if arg=='test':
            do_test()
            sys.exit(0)
        elif arg=='doc':
            do_doc()
            sys.exit(0)
        else:
            pass

    main()
