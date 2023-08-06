"""sharedfolder - Holds abstractions related to VirtualBox shared folders."""

from pyvb.constants import *
from pyvb.parser import *

class vbSharedFolderParser(vbParser):
    """A parser for parsing shared folder command line output."""
    def __init__(self):
        """Constructor.  Initialize the found attributes dictionary
        as well as the attributes we are looking for.
        @return: A new L{pyvb.sharedfolder.vbSharedFolderParser}
        @rtype: L{pyvb.sharedfolder.vbSharedFolderParser}"""
        self.found_attributes={}
        self.attributes={'name': VB_RE_SHAREDFOLDER_PATH,\
                         'path': VB_RE_SHAREDFOLDER_PATH}
                        
    def parse(self, file):
        """Parse the specified file and return the results.
        @param file: The file to parse.
        @type file: File/List
        @return: A list of L{pyvb.sharedfolder.vbSharedFolder} instances.
        @rtype: List"""
        shared_folders=[]
        for result in self._parse(file):
            found_folder=vbSharedFolder(name=result['name'],\
                                        path=result['path'])
            shared_folders.append(found_folder)
        return shared_folders

class vbSharedFolder:
    """An abstraction representing a VirtualBox shared folder."""
    def __init__(self, **kw):
        """Constructor.  Initialize attributes.
        @return: A new L{pyvb.sharedfolder.vbSharedFolder} instance.
        @rtype: L{pyvb.sharedfolder.vbSharedFolder}"""
        try:
            self.setName(kw['name'])
        except KeyError:
            self.setName('')
        try:
            self.setPath(kw['path'])
        except KeyError:
            self.setName('')
            
    def setName(self, name):
        """Set the name attribute of this L{pyvb.sharedfolder.vbSharedFolder} instance.
        @param name: The name attribute.
        @type name: String
        @return: None
        @rtype: None"""
        self.name=name
        
    def setPath(self, path):
        """Set the path attribute of this L{pyvb.sharedfolder.vbSharedFolder} instance.
        @param path: The path attribute.
        @type path: String
        @return: None
        @rtype: None"""
        self.path=path
        
    def getName(self):
        """Return the name attribute of this L{pyvb.sharedfolder.vbSharedFolder} instance.
        @return: The name attribute.
        @rtype: String"""
        return self.name
    
    def getPath(self):
        """Return the path attribute of this L{pyvb.sharedfolder.vbSharedFolder} instance.
        @return: The path attribute.
        @rtype: String"""
        return self.path