"""
hdd - pyvb module that holds the implementation of HDD related abstractions.
"""
from pyvb.constants import *
from pyvb.parser import *

class vbHddParser(vbParser):
    def __init__(self):
        self.found_attributes={}
        self.attributes={'uuid':VB_RE_UUID,\
                         'storagetype':VB_RE_STORAGETYPE,\
                         'path':VB_RE_PATH,\
                         'accessible':VB_RE_ACCESSIBLE,\
                         'usage':VB_RE_USAGE}
    
    def parse(self, file):
        hdds=[]
        for result in self._parse(file):
            found_hdd=vbHdd(uuid=result['uuid'],\
                            storagetype=result['storagetype'],\
                            path=result['path'],\
                            accessible=result['accessible'],\
                            usage=result['usage'])
            hdds.append(found_hdd)
        return hdds
    
class vbHdd:
    def __init__(self, **kw):
        try:
            self.setUUID(kw['uuid'])
        except KeyError:
            self.setUUID('')
        try:
            self.setStoragetype(kw['storagetype'])
        except KeyError:
            self.setStoragetype('')
        try:
            self.setPath(kw['path'])
        except KeyError:
            self.setPath('')
        try:
            self.setAccessible(kw['accessible'])
        except KeyError:
            self.setAccessible('')
        try:
            self.setUsage(kw['usage'])
        except KeyError:
            self.setUsage('')
            
    def setUUID(self, uuid):
        self.uuid=uuid
        
    def setStoragetype(self, storagetype):
        self.storagetype=storagetype
        
    def setPath(self, path):
        self.path=path
        
    def setAccessible(self, accessible):
        self.accessible=accessible
        
    def setUsage(self, usage):
        self.usage=usage
        
    def getUUID(self):
        return self.uuid
    
    def getStoragetype(self):
        return self.storagetype
    
    def getPath(self):
        return self.path
    
    def getAccessible(self):
        return self.accessible
    
    def getUsage(self):
        return self.usage