#!/usr/bin/python

import os

class walker( object ):
    def __init__(self,path,order=False) :
        self._path = path
        
    def __iter__(self) :
        self._result = []
        self._tmpresult = {}
        os.path.walk(self._path,walker.callback,self)
        
        self._index = len(self._result)
        return self
        
    def next(self) :
        if self._index > 0:
            self._index-=1
            # print self._result[self._index]
            return self._result[self._index]
        raise StopIteration
        
    def callback(self, path, files) :
        dirs = []
        fileonlys = []
        for file in files :
            if os.path.isdir(os.path.join(path,file)) :
                dirs.append(file)
            else : 
                fileonlys.append(file)
        self._tmpresult[path] = (path,dirs,fileonlys)
        self._result.append((path,dirs,fileonlys))
        
            
            
