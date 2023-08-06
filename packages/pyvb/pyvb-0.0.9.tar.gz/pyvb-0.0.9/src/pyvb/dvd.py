"""
dvd - pyvb module that holds the implementation of all DVD related abstractions.
"""
from pyvb.constants import *
from pyvb.parser import *

class vbHostDvdParser(vbParser):
    """A parser for parsing the command line output related to the host DVD."""
    def __init__(self):
        """Constructor.  Initialize the found attributes and the attributes
        we are looking for.
        @return: A new L{pyvb.dvd.vbHostDvdParser} instance.
        @rtype: L{pyvb.dvd.vbHostDvdParser}"""
        self.found_attributes={}
        self.attributes={'name':VB_RE_NAME}
        
    def parse(self, file):
        """Parse the specified file for a host DVD.
        @param file: The file to parse.
        @type file: File
        @return: A list of L{pyvb.dvd.vbHostDvd} instances.
        @rtype: List"""
        hostdvds=[]
        for result in self._parse(file):
            found_hostdvd=vbHostDvd(name=result['name'])
            hostdvds.append(found_hostdvd)
        return hostdvds
    
class vbDvdParser(vbParser):
    """A parser for parsing the command line output related to virtual machine
    DVDs."""
    def __init__(self):
        """Constructor.  Initialize the found attributes and the attributes
        we are looking for.
        @return: A new L{pyvb.dvd.vbDvdParser} instance.
        @rtype: L{pyvb.dvd.vbDvdParser}"""
        self.found_attributes={}
        self.attributes={'uuid':VB_RE_UUID,\
                         'path':VB_RE_PATH,\
                         'accessible':VB_RE_ACCESSIBLE}
    
    def parse(self, file):
        """Parse the specified file for a virtual machine DVD.
        @param file: The file to parse.
        @type file: File
        @return: A list of L{pyvb.dvd.vbDvd} instances.
        @rtype: List"""
        dvds=[]
        for result in self._parse(file):
            found_dvd=vbDvd(uuid=result['uuid'],\
                            path=result['path'],\
                            accessible=result['accessible'])
            dvds.append(found_dvd)
        return dvds
    
class vbHostDvd:
    """An abstraction representing a host DVD."""
    def __init__(self, **kw):
        """Constructor.  Initialize the attributes.
        @return: A new L{pyvb.dvd.vbHostDvd} instance.
        @rtype: L{pyvb.dvd.vbHostDvd}"""
        try:
            self.setName(kw['name'])
        except KeyError:
            self.setName('')
        
    def setName(self, name):
        """Set the name attribute of this L{pyvb.dvd.vbHostDvd} instance.
        @param name: The name attribute.
        @type name: String
        @return: None
        @rtype: None"""
        self.name=name
        
    def getName(self):
        """Return the name attribute of this L{pyvb.dvd.vbHostDvd} instenace.
        @return: The name attribute.
        @rtype: String"""
        return self.name
    
class vbDvd:
    """An abstraction representing a virtual machine DVD."""
    def __init__(self, **kw):
        """Constructor.  Initialize the attributes.
        @return: A new L{pyvb.dvd.vbDvd} instance.
        @rtype: L{pyvb.dvd.vbDvd}"""
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
        """Set the uuid attribute of this L{pyvb.dvd.vbDvd} instance.
        @param uuid: The uuid attribute.
        @type uuid: String
        @return: None
        @rtype: None"""
        self.uuid=uuid
        
    def setPath(self, path):
        """Set the path attribute of this L{pyvb.dvd.vbDvd} instance.
        @param path: The path attribute.
        @type path: String
        @return: None
        @rtype: None"""
        self.path=path
        
    def setAccessible(self, accessible):
        """Set the accessible attribute of this L{pyvb.dvd.vbDvd} instance.
        @param accessible: The accessible attribute.
        @type accessible: String
        @return: None
        @rtype: None"""
        self.accessible=accessible
        
    def getUUID(self):
        """Return the uuid attribute of this L{pyvb.dvd.vbDvd} instance.
        @return: The uuid attribute.
        @rtype: String"""
        return self.uuid
    
    def getPath(self):
        """Return the path attribute of this L{pyvb.dvd.vbDvd} instance.
        @return: The path attribute.
        @rtype: String"""
        return self.path
    
    def getAccessible(self):
        """Return the accessible attribute of this L{pyvb.dvd.vbDvd} instance.
        @return: The path attribute.
        @rtype: String"""
        return self.accessible