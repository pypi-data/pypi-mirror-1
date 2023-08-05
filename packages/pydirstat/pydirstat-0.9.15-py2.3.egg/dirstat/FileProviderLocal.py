#!/usr/bin/env python

import os
import walker
from FileProviderBase import StatInfoBase
from FileProviderBase import FileProviderBase

class FileProviderLocal(FileProviderBase) :
    """The local FileProvider.

    It use the os package to do its dirty job, so
    it may be quite portable."""

    supports_unicode_filenames = os.path.supports_unicode_filenames

    def __init__(self,url) :
        self._url = url
        self._walker = None
        if hasattr(os,'walk') :
            self._walker = os.walk
        else :
            self._walker = walker.walker
    def walk(self) :
        return self._walker(self._url,False)
    def split(self,path) :
        return os.path.split(path)
    def join(self,*args) :
        return os.path.join(*args)
    def abspath(self,path) :
        return os.path.abspath(path)
    def stat(self,file) :
        class StatInfo(StatInfoBase) :
            def __init__(self,file) :
                self._lstat = os.lstat(file)
            def st_dev(self) :
                return self._lstat.st_dev
            def st_mode(self) :
                return self._lstat.st_mode
            def st_nlink(self) :
                return self._lstat.st_nlink
            def st_mtime(self) :
                return self._lstat.st_mtime
            def st_size(self) :
                return self._lstat.st_size
            def st_blocks(self) :
                return getattr(self._lstat,'st_blocks',int(self._lstat.st_size/512L))
            def st_dev(self) :
                return self._lstat.st_dev
            def is_dir(self) :
                return os.path.stat.S_ISDIR ( self._lstat.st_mode )
            def is_reg(self) :
                return os.path.stat.S_ISREG ( self._lstat.st_mode )
            def is_lnk(self) :
                return os.path.stat.S_ISLNK ( self._lstat.st_mode )
            def is_blk(self) :
                return os.path.stat.S_ISBLK ( self._lstat.st_mode )
            def is_chr(self) :
                return os.path.stat.S_ISCHR ( self._lstat.st_mode )
            def is_fifo(self) :
                return os.path.stat.S_ISFIFO ( self._lstat.st_mode )
            def is_sock(self) :
                return os.path.stat.S_ISSOCK ( self._lstat.st_mode )

        return StatInfo(file)
