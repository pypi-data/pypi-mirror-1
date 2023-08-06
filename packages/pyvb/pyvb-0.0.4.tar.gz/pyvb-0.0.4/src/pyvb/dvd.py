"""
dvd - pyvb module that holds the implementation of all DVD related abstractions.
"""
from pyvb.constants import *
from pyvb.parser import *

class vbHostDvdParser(vbParser):
    def __init__(self):
        self.found_attributes={}
        self.attributes={'name':VB_RE_NAME}
        
    def parse(self, file):
        hostdvds=[]
        for result in self._parse(file):
            found_hostdvd=vbHostDvd(name=result['name'])
            hostdvds.append(found_hostdvd)
        return hostdvds
    
class vbDvdParser(vbParser):
    def __init__(self):
        self.found_attributes={}
        self.attributes={'uuid':VB_RE_UUID,\
                         'path':VB_RE_PATH,\
                         'accessible':VB_RE_ACCESSIBLE}
    
    def parse(self, file):
        dvds=[]
        for result in self._parse(file):
            found_dvd=vbDvd(uuid=result['uuid'],\
                            path=result['path'],\
                            accessible=result['accessible'])
            dvds.append(found_dvd)
        return dvds
    
class vbHostDvd:
    def __init__(self, **kw):
        try:
            self.setName(kw['name'])
        except KeyError:
            self.setName('')
        
    def setName(self, name):
        self.name=name
        
    def getName(self):
        return self.name
    
class vbDvd:
    def __init__(self, **kw):
        try:
            self.setUUID(kw['uuid'])
        except KeyError:
            self.setUUID('')
        try:
            self.setPath(kw['path'])
        except KeyError:
            self.setPath('')
        try:
            self.setAccessible(kw['accessible'])
        except KeyError:
            self.setAccessible('')
            
    def setUUID(self, uuid):
        self.uuid=uuid
        
    def setPath(self, path):
        self.path=path
        
    def setAccessible(self, accessible):
        self.accessible=accessible
        
    def getUUID(self):
        return self.uuid
    
    def getPath(self):
        return self.path
    
    def getAsscessible(self):
        return self.accessible