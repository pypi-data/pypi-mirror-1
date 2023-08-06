"""
hdd - pyvb module that holds the implementation of HDD related abstractions.
"""
from pyvb.constants import *
from pyvb.parser import *

class vbHddParser(vbParser):
    """A parser for parsing the command line output related to HDDs."""
    def __init__(self):
        """Constructor.  Initialize the found attributes dictionary as 
        well as the attributes we are looking for.
        @return: A new L{pyvb.hdd.vbHddParser} instance.
        @rtype: L{pyvb.hdd.vbHddParser}"""
        self.found_attributes={}
        self.attributes={'uuid':VB_RE_UUID,\
                         'storagetype':VB_RE_STORAGETYPE,\
                         'path':VB_RE_PATH,\
                         'accessible':VB_RE_ACCESSIBLE,\
                         'usage':VB_RE_USAGE}
    
    def parse(self, file):
        """Parse the specified file and return a list of results.
        @param file: The file to parse.
        @type file: File/List
        @return: A list of L{pyvb.hdd.vbHdd} instances.
        @rtype: List"""
        hdds=[]
        for result in self._parse(file):
            found_hdd=vbHdd()
            try:
                found_hdd.setUUID(result['uuid'])
            except KeyError:
                pass
            try:
                found_hdd.setStoragetype(result['storagetype'])
            except KeyError:
                pass
            try:
                found_hdd.setPath(result['path'])
            except KeyError:
                pass
            try:
                found_hdd.setAccessible(result['accessible'])
            except KeyError:
                pass
            try:
                found_hdd.setUsage(result['usage'])
            except KeyError:
                pass
            hdds.append(found_hdd)
        return hdds
    
    def parseSingle(self, file):
        self.removeAttribute('usage')
        hdds=[]
        for result in self._parse(file):
            found_hdd=vbHdd(uuid=result['uuid'],\
                            storagetype=result['storagetype'],\
                            path=result['path'],\
                            accessible=result['accessible'])
            hdds.append(found_hdd)
        return hdds
    
class vbHdd:
    """An abstraction representing an HDD in VirtualBox."""
    def __init__(self, **kw):
        """Constructor.  Initialize the attributes.
        @return: A new L{pyvb.hdd.vbHdd} instance.
        @rtype: L{pyvb.hdd.vbHdd}"""
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
        try:
            self.setRegistered(kw['registered'])
        except KeyError:
            self.setRegistered('')
        try:
            self.setSize(kw['size'])
        except KeyError:
            self.setSize('')
        try:
            self.setDiskSize(kw['disksize'])
        except KeyError:
            self.setDiskSize('')
            
    def setUUID(self, uuid):
        """Set the uuid attribute of this L{pyvb.hdd.vbHdd} instance.
        @param uuid: The uuid attribute.
        @type uuid: String
        @return: None
        @rtype: None"""
        self.uuid=uuid
        
    def setStoragetype(self, storagetype):
        """Set the storagetype attribute of this L{pyvb.hdd.vbHdd} instance.
        @param storagetype: The storagetype attribute.
        @type storagetype: String
        @return: None
        @rtype: None"""
        self.storagetype=storagetype
        
    def setPath(self, path):
        """Set the path attribute of this L{pyvb.hdd.vbHdd} instance.
        @param path: The path attribute.
        @type path: String
        @return: None
        @rtype: None"""
        self.path=path
        
    def setAccessible(self, accessible):
        """Set the accessible attribute of this L{pyvb.hdd.vbHdd} instance.
        @param accessible: The accessible attribute.
        @type accessible: String
        @return: None
        @rtype: None"""
        self.accessible=accessible
        
    def setUsage(self, usage):
        """Set the usage attribute of this L{pyvb.hdd.vbHdd} instance.
        @param usage: The usage attribute.
        @type usage: String
        @return: None
        @rtype: None"""
        self.usage=usage
        
    def setRegistered(self, registered):
        self.registered=registered
        
    def setSize(self, size):
        self.size=size
        
    def setDiskSize(self, disksize):
        self.disksize=disksize
        
    def getUUID(self):
        """Return the uuid attribute of this L{pyvb.hdd.vbHdd} instance.
        @return: The uuid attribute.
        @rtype: String"""
        return self.uuid
    
    def getStoragetype(self):
        """Return the storagetype attribute of this L{pyvb.hdd.vbHdd} instance.
        @return: The storagetype attribute.
        @rtype: String"""
        return self.storagetype
    
    def getPath(self):
        """Return the path attribute of this L{pyvb.hdd.vbHdd} instance.
        @return: The path attribute.
        @rtype: String"""
        return self.path
    
    def getAccessible(self):
        """Return the accessible attribute of this L{pyvb.hdd.vbHdd} instance.
        @return: The accessible attribute.
        @rtype: String"""
        return self.accessible
    
    def getUsage(self):
        """Return the usage attribute of this L{pyvb.hdd.vbHdd} instance.
        @return: The usage attribute.
        @rtype: String"""
        return self.usage
    
    def getRegistered(self):
        return self.registered
    
    def getSize(self):
        return self.size
    
    def getDiskSize(self):
        return self.disksize