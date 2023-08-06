"""
ostype - pyvb module that holds all operating system type related abstractions.
"""
from pyvb.constants import *
from pyvb.parser import *

class vbOsTypeParser(vbParser):
    def __init__(self):
        self.found_attributes={}
        self.attributes={'id':VB_RE_ID,\
                         'description':VB_RE_DESCRIPTION}
                        
    def parse(self, file):
        ostypes=[]
        for result in self._parse(file):
            found_os=vbOsType(id=result['id'],\
                              description=result['description'])
            ostypes.append(found_os)
        return ostypes
    
class vbOsType:
    def __init__(self, **kw):
        try:
            self.setID(kw['id'])
        except KeyError:
            self.setID('')
        try:
            self.setDescription(kw['description'])
        except KeyError:
            self.setDescription('')
    
    def setID(self, id):
        self.id=id
        
    def setDescription(self, description):
        self.description=description
        
    def getID(self):
        return self.id
    
    def getDescription(self):
        return self.description