"""sharedfolder - Holds abstractions related to VirtualBox shared folders."""

from pyvb.constants import *
from pyvb.parser import *

class vbSharedFolderParser(vbParser):
    def __init__(self):
        self.found_attributes={}
        self.attributes={'name': VB_RE_SHAREDFOLDER_PATH,\
                         'path': VB_RE_SHAREDFOLDER_PATH}
                        
    def parse(self, file):
        shared_folders=[]
        for result in self._parse(file):
            found_folder=vbSharedFolder(name=result['name'],\
                                        path=result['path'])
            shared_folders.append(found_folder)
        return shared_folders

class vbSharedFolder:
    def __init__(self, **kw):
        try:
            self.setName(kw['name'])
        except KeyError:
            self.setName('')
        try:
            self.setPath(kw['path'])
        except KeyError:
            self.setName('')
            
    def setName(self, name):
        self.name=name
        
    def setPath(self, path):
        self.path=path
        
    def getName(self):
        return self.name
    
    def getPath(self):
        return self.path