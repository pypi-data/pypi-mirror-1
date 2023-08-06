"""state - Holds abstractions related to VirtualMachine states."""

from pyvb.constants import *
from pyvb.parser import *

class vbStateParser(vbParser):
    def __init__(self):
        self.found_attributes={}
        self.attributes={'name': VB_RE_STATE_NAME,\
                         'date': VB_RE_STATE_DATE}
                        
    def parse(self, file):
        states=[]
        for result in self._parse(file):
            found_state=vbState(name=result['name'],\
                                date=result['date'])
            states.append(found_state)
        return states

class vbState:
    def __init__(self, **kw):
        try:
            self.setName(kw['name'])
        except KeyError:
            self.setName('')
        try:
            self.setDate(kw['date'])
        except KeyError:
            self.setDate('')
            
    def setName(self, name):
        self.name=name
        
    def setDate(self, date):
        self.date=date
        
    def getName(self):
        return self.name
    
    def getDate(self):
        return self.date