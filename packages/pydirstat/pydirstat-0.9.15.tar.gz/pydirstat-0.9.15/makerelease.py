#!/usr/bin/env python

import string
import os
import shutil
import setup
import sys
import getopt

if not(os.path.exists('REPOUSER')) :
    print 'What is your repository user name?'
    #print 'What is your quest?'
    #print 'What is the capital of Asyria?'
    username = sys.stdin.readline()
    open("REPOUSER","wt").write(username)

version=string.strip(open("VERSION").readline())
user=string.strip(open("REPOUSER").readline())
repository='svn+ssh://%(user)s@svn.berlios.de/svnroot/repos/pydirstat/pydirstat' % {'user':user}
public_repository='svn://svn.berlios.de/pydirstat/pydirstat'
tmpdir='tmp'
# Gruik
nsisexe=r'C:\Program Files\NSIS\makensisw.exe'

scriptargs = {
    'version':version,
    'user':user,
    'repository':repository,
    'public_repository':public_repository,
    'tmpdir':tmpdir,
    'nsisexe':nsisexe,
    }

def create_tag():
    commands = [
        'svn up',
        'svn cp -m "Release %(version)s" . %(repository)s/tags/%(version)s' % scriptargs,
        ]

    for command in commands :
        os.system(command)

def create_dist():
    if os.path.exists(tmpdir):
        shutil.rmtree(tmpdir)
    if os.path.exists('build'):
        shutil.rmtree('build')
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    os.mkdir(tmpdir)

    sys.argv=['setup.py','sdist','--dist-dir=.','--format=gztar']
    setup.main()
    shutil.move("%s-%s.tar.gz"%(setup.pkgname,setup.version),tmpdir)

    sys.argv=['setup.py','bdist_egg','--dist-dir=.']
    setup.main()
    shutil.move("%s-%s-py%s.egg"%(setup.pkgname,setup.version,"%d.%d"%sys.version_info[0:2]),tmpdir)

    sys.argv=['setup.py','py2exe']
    setup.main()
    os.system('"%(nsisexe)s" nsis\\pydirstat.nsi' % scriptargs)
    shutil.move(os.path.join("nsis","pyDirStat-%s.exe"%setup.version),tmpdir)


    if os.path.exists('build'):
        shutil.rmtree('build')
    if os.path.exists('dist'):
        shutil.rmtree('dist')

def make_version_files():

    # src/dirstat/__version__.py : version for python module

    handle = open(os.path.join('src','dirstat','__version__.py'),'wt')
    handle.write('__version__ = "%s"\n' % version)
    handle.close()

    # src/dirstat/__version__.py : version for NSIS Windows-installer

    handle = open(os.path.join('nsis','version.nsi'),'wt')
    handle.write('!define PRODUCT_VERSION "%s"\n' % version)
    handle.write('!define PYTHON_VERSION "%d.%d"\n' % sys.version_info[:2])
    handle.close()

    # setup.py use it's own way to read VERSION

def main():
    for arg in sys.argv[1:] :
        if arg=='version' :
            print "Creating version files"
            print "----------------------"
            make_version_files()
        if arg=='tag' :
            print "Creating tag"
            print "------------"
            create_tag()
        if arg=='dist' :
            print "Creating dist files"
            print "-------------------"
            create_dist()

main()
