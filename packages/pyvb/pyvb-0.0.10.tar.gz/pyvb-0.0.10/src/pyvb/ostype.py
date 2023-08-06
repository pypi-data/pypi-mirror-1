"""
ostype - pyvb module that holds all operating system type related abstractions.
"""
from pyvb.constants import *
from pyvb.parser import *

class vbOsTypeParser(vbParser):
    """A parser for parsing command line output related to OS types."""
    def __init__(self):
        """Constructor.  Initialize the found attributes dictionary as well
        as the attributes we are looking for.
        @return: A new L{pyvb.ostype.vbOsTypeParser} instance.
        @rtype: L{pyvb.ostype.vbOsTypeParser}"""
        self.found_attributes={}
        self.negated_attributes=[]
        self.attributes={'id':VB_RE_ID,\
                         'description':VB_RE_DESCRIPTION}
                        
    def parse(self, file):
        """Parse the specified file and return the results.
        @param file: The file we are parsing.
        @type file: File/List
        @return: A list of L{pyvb.ostype.vbOsType} instances.
        @rtype: List"""
        ostypes=[]
        for result in self._parse(file):
            found_os=vbOsType(id=result['id'],\
                              description=result['description'])
            ostypes.append(found_os)
        return ostypes
    
class vbOsType:
    """An abstraction representing the OS type of a virtual machine."""
    def __init__(self, **kw):
        """Constructor.  Initialize the attributes.
        @return: A new L{pyvb.ostype.vbOsType} instance.
        @rtype: L{pyvb.ostype.vbOsType}"""
        try:
            self.setID(kw['id'])
        except KeyError:
            self.setID('')
        try:
            self.setDescription(kw['description'])
        except KeyError:
            self.setDescription('')
    
    def setID(self, id):
        """Set the id attribute of this L{pyvb.ostype.vbOsType} instance.
        @param id: The id attribute.
        @type id: String
        @return: None
        @rtype: None"""
        self.id=id
        
    def setDescription(self, description):
        """Set the description attribute of this L{pyvb.ostype.vbOsType} 
        instance.
        @param description: The description attribute.
        @type description: String
        @return: None
        @rtype: None"""
        self.description=description
        
    def getID(self):
        """Return the id attribute of this L{pyvb.ostype.vbOsType} instance.
        @return: The id attribute.
        @rtype: String"""
        return self.id
    
    def getDescription(self):
        """Return the description attribute of this L{pyvb.ostype.vbOsType}
        instance.
        @return: The description attribute.
        @rtype: String"""
        return self.description