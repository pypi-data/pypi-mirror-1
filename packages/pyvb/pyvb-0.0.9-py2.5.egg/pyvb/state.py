"""state - Holds abstractions related to VirtualMachine states."""

from pyvb.constants import *
from pyvb.parser import *

class vbStateParser(vbParser):
    """A parser for parsing machine state command line output."""
    def __init__(self):
        """Constructor.  Initialize the found attributes dictionary
        as well as the attributes we are looking for.
        @return: A new L{pyvb.state.vbStateParser} instance.
        @rtype: L{pyvb.state.vbStateParser}"""
        self.found_attributes={}
        self.attributes={'name': VB_RE_STATE_NAME,\
                         'date': VB_RE_STATE_DATE}
                        
    def parse(self, file):
        """Parse the specified file and return the results.
        @param file: The file to parse.
        @type file: File/List
        @return: A list of L{pyvb.state.vbState} instances.
        @rtype: List"""
        states=[]
        for result in self._parse(file):
            found_state=vbState(name=result['name'],\
                                date=result['date'])
            states.append(found_state)
        return states

class vbState:
    """An abstraction representing a VirtualBox machine state."""
    def __init__(self, **kw):
        """Constructor.  Initialize the attributes.
        @return: A new L{pyvb.state.vbState} instance.
        @rtype: L{pyvb.state.vbState}"""
        try:
            self.setName(kw['name'])
        except KeyError:
            self.setName('')
        try:
            self.setDate(kw['date'])
        except KeyError:
            self.setDate('')
            
    def setName(self, name):
        """Set the name attribute of this L{pyvb.state.vbState} instance.
        @param name: The name attribute.
        @type name: String
        @return: None
        @rtype: None"""
        self.name=name
        
    def setDate(self, date):
        """Set the date attribute of this L{pyvb.state.vbState} instance.
        @param date: The date attribute.
        @type date: String
        @return: None
        @rtype: None"""
        self.date=date
        
    def getName(self):
        """Return the name attribute of this L{pyvb.state.vbState} instance.
        @return: The name attribute.
        @rtype: String"""
        return self.name
    
    def getDate(self):
        """Return the date attribute of this L{pyvb.state.vbState} instance.
        @return: The date attribute.
        @rtype: String"""
        return self.date