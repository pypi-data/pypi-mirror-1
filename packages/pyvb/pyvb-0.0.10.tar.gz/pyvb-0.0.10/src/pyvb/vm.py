"""
vm - pyvb module that holds the implementation of all VM related abstractions.
"""
from pyvb.constants import *
from pyvb.parser import *
from pyvb.command import *
from pyvb.sharedfolder import *
from pyvb.state import *
from pyvb.hdd import *

class vbVmParser(vbParser):
    """A parser for parsing the command line output for VirtualBox VMs."""
    def __init__(self):
        """Constructor.  Initialize the found atributes dictionary which
        holds the attributes that are found and initialize the dictionary
        which contains the attribute we are looking for.
        @return: A new instance.
        @rtype: L{pyvb.vbVmParser}"""
        self.found_attributes={}
        self.negated_attributes=['primarymaster']
        self.attributes={'name':VB_RE_NAME,\
                         'guestos':VB_RE_GUESTOS,\
                         'uuid':VB_RE_UUID,\
                         'configfile':VB_RE_CONFIGFILE,\
                         'memorysize':VB_RE_MEMORYSIZE,\
                         'vramsize':VB_RE_VRAMSIZE,
                         'bootmenumode':VB_RE_BOOTMENUMODE,\
                         'acpi':VB_RE_ACPI,\
                         'ioacpi':VB_RE_IOACPI,\
                         'timeoffset':VB_RE_TIMEOFFSET,\
                         'virtext':VB_RE_VIRTEXT,\
                         'state':VB_RE_STATE,\
                         'monitorcount':VB_RE_MONITORCOUNT,\
                         'floppy':VB_RE_FLOPPY,\
                         'primarymaster':VB_RE_PRIMARYMASTER,\
                         'dvd':VB_RE_DVD,\
                         'nic1':VB_RE_NIC1,\
                         'nic2':VB_RE_NIC2,\
                         'nic3':VB_RE_NIC3,\
                         'nic4':VB_RE_NIC4,\
                         'uart1':VB_RE_UART1,\
                         'uart2':VB_RE_UART2,\
                         'audio':VB_RE_AUDIO,\
                         'clipboardmode':VB_RE_CLIPBOARDMODE,\
                         'sharedfolders':VB_RE_SHAREDFOLDERS}
               
    def parse(self, file):
        """Parse the given file.  For each VM that is found,
        we append the result to the list of returned VMs.
        @param file: The file object to parse.
        @type file: File
        @return: The list of L{pyvb.vm.vbVM} instances.
        @rtype: List"""
        vms=[]
        for result in self._parse(file):
            found_vm=vbVM()
            try:
                found_vm.setName(result['name'])
            except KeyError:
                pass
            try:
                found_vm.setGuestOS(result['guestos'])
            except KeyError:
                pass
            try:
                found_vm.setUUID(result['uuid'])
            except KeyError:
                pass
            try:
                found_vm.setConfigFile(result['configfile'])
            except KeyError:
                pass
            try:
                found_vm.setMemorySize(result['memorysize'])
            except KeyError:
                pass
            try:
                found_vm.setVramSize(result['vramsize'])
            except KeyError:
                pass
            try:
                found_vm.setBootMenuMode(result['bootmenumode'])
            except KeyError:
                pass
            try:
                found_vm.setACPI(result['acpi'])
            except KeyError:
                pass
            try:
                found_vm.setIOACPI(result['ioacpi'])
            except KeyError:
                pass
            try:
                found_vm.setTimeOffset(result['timeoffset'])
            except KeyError:
                pass
            try:
                found_vm.setVirtExt(result['virtext'])
            except KeyError:
                pass
            try:
                found_vm.setState(result['state'])
            except KeyError:
                pass
            try:
                found_vm.setMonitorCount(result['monitorcount'])
            except KeyError:
                pass
            try:
                found_vm.setFloppy(result['floppy'])
            except KeyError:
                pass
            try:
                found_vm.setPrimaryMaster(result['primarymaster'])
            except KeyError:
                pass
            try:
                found_vm.setDVD(result['dvd'])
            except KeyError:
                pass
            try:
                found_vm.setNIC1(result['nic1'])
            except KeyError:
                pass
            try:
                found_vm.setNIC2(result['nic2'])
            except KeyError:
                pass
            try:
                found_vm.setNIC3(result['nic3'])
            except KeyError:
                pass
            try:
                found_vm.setNIC4(result['nic4'])
            except KeyError:
                pass
            try:
                found_vm.setUART1(result['uart1'])
            except KeyError:
                pass
            try:
                found_vm.setUART2(result['uart2'])
            except KeyError:
                pass
            try:
                found_vm.setClipboardMode(result['clipboardmode'])
            except KeyError:
                pass
            try:
                found_vm.setSharedFolders(result['sharedfolders'])
            except KeyError:
                pass
            vms.append(found_vm)
        return vms
    
    def parseHddUUID(self, hdd):
        """Parse the specified HDD and return the uuid.
        @param hdd: The hdd string to parse.
        @type hdd: String
        @return: The uuid of the specified HDD.
        @rtype: String"""
        return VB_RE_UUID2.match(hdd).groups()[1]
    
    def parseState(self, state):
        """Parse the specified machine state and return a tuple
        containing the state name, and the state date.
        @param state: The state string to parse.
        @type state: String
        @return: A tuple containing the state components.
        @rtype: Tuple"""
        return VB_RE_STATE2.match(state).groups()
    
class vbVM:
    """An abstraction representing a virtual machine in VirtualBox."""
    def __init__(self, **kw):
        """Constructor.  Initialize attributes.
        @return: A new instance.
        @rtype: L{pyvb.vm.vbVM}"""
        try:
            self.setName(kw['name'])
        except KeyError:
            self.setName('')
        try:
            self.setGuestOS(kw['guestos'])
        except KeyError:
            self.setGuestOS('')
        try:
            self.setUUID(kw['uuid'])
        except KeyError:
            self.setUUID('')
        try:
            self.setConfigFile(kw['configfile'])
        except KeyError:
            self.setConfigFile('')
        try:
            self.setMemorySize(kw['memorysize'])
        except KeyError:
            self.setMemorySize('')
        try:
            self.setVramSize(kw['vramsize'])
        except Exception, e:
            self.setVramSize('')
        try:
            self.setBootMenuMode(kw['bootmenumode'])
        except KeyError:
            self.setBootMenuMode('')
        try:
            self.setACPI(kw['acpi'])
        except KeyError:
            self.setACPI('')
        try:
            self.setIOACPI(kw['ioacpi'])
        except KeyError:
            self.setIOACPI('')
        try:
            self.setTimeOffset(kw['timeoffset'])
        except KeyError:
            self.setTimeOffset('')
        try:
            self.setVirtExt(kw['virtext'])
        except KeyError:
            self.setVirtExt('')
        try:
            self.setState(kw['state'])
        except KeyError:
            self.setState('')
        try:
            self.setMonitorCount(kw['monitorcount'])
        except KeyError:
            self.setMonitorCount('')
        try:
            self.setFloppy(kw['floppy'])
        except KeyError:
            self.setFloppy('')
        try:
            self.setPrimaryMaster(kw['primarymaster'])
        except KeyError:
            self.setPrimaryMaster('')
        try:
            self.setDVD(kw['dvd'])
        except KeyError:
            self.setDVD('')
        try:
            self.setNIC1(kw['nic1'])
        except KeyError:
            self.setNIC1('')
        try:
            self.setNIC2(kw['nic2'])
        except KeyError:
            self.setNIC2('')
        try:
            self.setNIC3(kw['nic3'])
        except KeyError:
            self.setNIC3('')
        try:
            self.setNIC4(kw['nic4'])
        except KeyError:
            self.setNIC4('')
        try:
            self.setUART1(kw['uart1'])
        except KeyError:
            self.setUART1('')
        try:
            self.setUART2(kw['uart2'])
        except KeyError:
            self.setUART2('')
        try:
            self.setAudio(kw['audio'])
        except KeyError:
            self.setAudio('')
        try:
            self.setClipboardMode(kw['clipboardmode'])
        except KeyError:
            self.setClipboardMode('')
        try:
            self.setSharedFolders(kw['sharedfolders'])
        except KeyError:
            self.setSharedFolders('')     
    
    def setName(self, name):
        """Set the name attribute of this L{pyvb.vm.vbVM} instance.
        @param name: The name attribute.
        @type name: String
        @return: None
        @rtype: None"""
        self.name=name
        
    def setGuestOS(self, guestos):
        """Set the guestos attribute of this L{pyvb.vm.vbVM} instance.
        @param guestos: The guestos attribute.
        @type guestos: String
        @return: None
        @rtype: None"""
        self.guestos=guestos
        
    def setUUID(self, uuid):
        """Set the uuid attribute of this L{pyvb.vm.vbVM} instance.
        @param uuid: The uuid attribute.
        @type uuid: String
        @return: None
        @rtype: None"""
        self.uuid=uuid
        
    def setConfigFile(self, configfile):
        """Set the configfile attribute of this L{pyvb.vm.vbVM} instance.
        @param configfile: The configfile attribute.
        @type configfile: String
        @return: None
        @rtype: None"""
        self.configfile=configfile
        
    def setMemorySize(self, memorysize):
        """Set the memorysize attribute of this L{pyvb.vm.vbVM} instance.
        @param memorysize: The memorysize attribute.
        @type memorysize: String
        @return: None
        @rtype: None"""
        self.memorysize=memorysize
        
    def setVramSize(self, vramsize):
        """Set the vramsize attribute of this L{pyvb.vm.vbVM} instance.
        @param vramsize: The vramsize attribute.
        @type vramsize: String
        @return: None
        @rtype: None"""
        self.vramsize=vramsize
        
    def setBootMenuMode(self, bootmenumode):
        """Set the bootmenumode attribute of this L{pyvb.vm.vbVM} instance.
        @param bootmenumode: The bootmenumode attribute.
        @type bootmenumode: String
        @return: None
        @rtype: None"""
        self.bootmenumode=bootmenumode
        
    def setACPI(self, acpi):
        """Set the acpi attribute of this L{pyvb.vm.vbVM} instance.
        @param acpi: The acpi attribute.
        @type acpi: String
        @return: None
        @rtype: None"""
        self.acpi=acpi
        
    def setIOACPI(self, ioacpi):
        """Set the ioacpi attribute of this L{pyvb.vm.vbVM} instance.
        @param ioacpi: The ioacpi attribute.
        @type ioacpi: String
        @return: None
        @rtype: None"""
        self.ioacpi=ioacpi
        
    def setTimeOffset(self, timeoffset):
        """Set the timeoffset attribute of this L{pyvb.vm.vbVM} instance.
        @param timeoffset: The timeoffset attribute.
        @type timeoffset: String
        @return: None
        @rtype: None"""
        self.timeoffset=timeoffset
        
    def setVirtExt(self, virtext):
        """Set the virtext attribute of this L{pyvb.vm.vbVM} instance.
        @param virtext: The virtext attribute of this L{pyvb.vm.vbVM} instance.
        @type virtext: String
        @return: None
        @rtype: None"""
        self.virtext=virtext
        
    def setState(self, state):
        """Set the state attribute of this L{pyvb.vm.vbVM} instance.
        @param state: The state attribute.
        @type state: String
        @return: None
        @rtype: None"""
        self.state=state
        
    def setMonitorCount(self, monitorcount):
        """Set the monitorcount attribute of this L{pyvb.vm.vbVM} instance.
        @param monitorcount: The monitorcount attribute.
        @type monitorcount: String
        @return: None
        @rtype: None"""
        self.monitorcount=monitorcount
        
    def setFloppy(self, floppy):
        """Set the floppy attribute of this L{pyvb.vm.vbVM} instance.
        @param floppy: The floppy attribute.
        @type floppy: String
        @return: None
        @rtype: None"""
        self.floppy=floppy
        
    def setPrimaryMaster(self, primarymaster):
        """Set the primarymaster attribute of this L{pyvb.vm.vbVM} instance.
        @param primarymaster: The primarymaster attribute.
        @type primarymaster: String
        @return: None
        @rtype: None"""
        self.primarymaster=primarymaster
        
    def setDVD(self, dvd):
        """Set the dvd attribute of this L{pyvb.vm.vbVM} instance.
        @param dvd: The dvd attribute.
        @type dvd: String
        @return: None
        @rtype: None"""
        self.dvd=dvd
        
    def setNIC1(self, nic1):
        """Set the nic1 attribute of this L{pyvb.vm.vbVM} instance.
        @param nic1: The nic1 attribute.
        @type nic1: String
        @return: None
        @rtype: None"""
        self.nic1=nic1
        
    def setNIC2(self, nic2):
        """Set the nic2 attribute of this L{pyvb.vm.vbVM} instance.
        @param nic2: The nic2 attribute.
        @type nic2: String
        @return: None
        @rtype: None"""
        self.nic2=nic2
        
    def setNIC3(self, nic3):
        """Set the nic3 attribute of this L{pyvb.vm.vbVM} instance.
        @param nic3: The nic3 attribute.
        @type nic3: String
        @return: None
        @rtype: None"""
        self.nic3=nic3
        
    def setNIC4(self, nic4):
        """Set the nic4 attribute of this L{pyvb.vm.vbVM} instance.
        @param nic4: The nic4 attribute.
        @type nic4: String
        @return: None
        @rtype: None"""
        self.nic4=nic4
        
    def setUART1(self, uart1):
        """Set the uart attribute of this L{pyvb.vm.vbVM} instance.
        @param uart1: The uart1 attribute.
        @type uart1: String
        @return: None
        @rtype: None"""
        self.uart1=uart1
        
    def setUART2(self, uart2):
        """Set the uart2 attribute of this L{pyvb.vm.vbVM} instance.
        @param uart2: The uart2 attribute.
        @type uart2: String
        @return: None
        @rtype: None"""
        self.uart2=uart2
        
    def setAudio(self, audio):
        """Set the audio attribute of this L{pyvb.vm.vbVM} instance.
        @param audio: The audio attribute.
        @type audio: String
        @return: None
        @rtype: None"""
        self.audio=audio
        
    def setClipboardMode(self, clipboardmode):
        """Set the clipboardmode attribute of this L{pyvb.vm.vbVM} instance.
        @param clipboardmode: The clipboardmode attribute.
        @type clipboardmode: String
        @return: None
        @rtype: None"""
        self.clipboardmode=clipboardmode
        
    def setSharedFolders(self, sharedfolders):
        """Set the sharedfolders attribute of this L{pyvb.vm.vbVM} instance.
        @param sharedfolders: The sharedfolders attribute.
        @type sharedfolders: String
        @return: None
        @rtype: None"""
        self.sharedfolders=sharedfolders
        
    def getName(self):
        """Return the name attribute of this L{pyvb.vm.vbVM} instance.
        @return: The name attribute.
        @rtype: String"""
        return self.name
    
    def getGuestOS(self):
        """Return the guestos attribute of this L{pyvb.vm.vbVM} instance.
        @return: The guestos attribute.
        @rtype: String"""
        return self.guestos
    
    def getUUID(self):
        """Return the uuid attribute of this L{pyvb.vm.vbVM} instance.
        @return: The uuid attribute.
        @rtype: String"""
        return self.uuid
    
    def getConfigFile(self):
        """Return the configfile attribute of this L{pyvb.vm.vbVM} instance.
        @return: The configfile attribute.
        @rtype: String"""
        return self.configfile
    
    def getMemorySize(self):
        """Return the memorysize attribute of this L{pyvb.vm.vbVM} instance.
        @return: The memorysize attribute.
        @rtype: String"""
        return self.memorysize
    
    def getVramSize(self):
        """Return the vramsize attribute of this L{pyvb.vm.vbVM} instance.
        @return: The vramsize attribute.
        @rtype: String"""
        return self.vramsize
    
    def getBootMenuMode(self):
        """Return the bootmenumode attribute of this L{pyvb.vm.vbVM} instance.
        @return: The bootmenumode attribute.
        @rtype: String"""
        return self.bootmenumode
    
    def getACPI(self):
        """Return the acpi attribute of this L{pyvb.vm.vbVM} instance.
        @return: The acpi attribute.
        @rtype: String"""
        return self.acpi
    
    def getIOACPI(self):
        """Return the ioacpi attribute of this L{pyvb.vm.vbVM} instance.
        @return: The ioacpi attribute.
        @rtype: String"""
        return self.ioacpi
    
    def getTimeOffset(self):
        """Return the timeoffset attribute of this L{pyvb.vm.vbVM} instance.
        @return: The timeoffset attribute.
        @rtype: String"""
        return self.timeoffset
    
    def getVirtExt(self):
        """Return the virtext attribute of this L{pyvb.vm.vbVM} instance.
        @return: The virtext attribute.
        @rtype: String"""
        return self.virtext
    
    def getState(self):
        """Return the state attribute of this L{pyvb.vm.vbVM} instance.
        @return: The state attribute.
        @rtype: String"""
        parser=vbStateParser()
        return parser.parse([' %s'%(self.state)])[0]
    
    def getMonitorCount(self):
        """Return the monitorcount attribute of this L{pyvb.vm.vbVM} instance.
        @return: The monitorcount attribute.
        @rtype: String"""
        return self.monitorcount
    
    def getFloppy(self):
        """Return the floppy attribute of this L{pyvb.vm.vbVM} instance.
        @return: The floppy attribute.
        @rtype: String"""
        return self.floppy
    
    def getPrimaryMaster(self):
        """Return the primarymaster attribute of this L{pyvb.vm.vbVM} instance.
        @return: The primarymaster attribute.
        @rtype: String"""
        return self.primarymaster
    
    def getDVD(self):
        """Return the dvd attribute of this L{pyvb.vm.vbVM} instance.
        @return: The dvd attribute.
        @rtype: String"""
        return self.dvd
    
    def getNIC1(self):
        """Return the nic1 attribute of this L{pyvb.vm.vbVM} instance.
        @return: The nic1 attribute.
        @rtype: String"""
        return self.nic1
    
    def getNIC2(self):
        """Return the nic2 attribute of this L{pyvb.vm.vbVM} instance.
        @return: The nic2 attribute.
        @rtype: String"""
        return self.nic2
    
    def getNIC3(self):
        """Return the nic3 attribute of this L{pyvb.vm.vbVM} instance.
        @return: The nic3 attribute.
        @rtype: String"""        
        return self.nic3
    
    def getNIC4(self):
        """Return the nic4 attribute of this L{pyvb.vm.vbVM} instance.
        @return: The nic4 attribute.
        @rtype: String"""        
        return self.nic4
    
    def getUART1(self):
        """Return the uart1 attribute of this L{pyvb.vm.vbVM} instance.
        @return: The uart1 attribute.
        @rtype: String"""
        return self.uart1
    
    def getUART2(self):
        """Return the uart2 attribute of this L{pyvb.vm.vbVM} instance.
        @return: The uart2 attribute.
        @rtype: String"""
        return self.uart2
    
    def getAudio(self):
        """Return the audio attribute of this L{pyvb.vm.vbVM} instance.
        @return: The audio attribute.
        @rtype: String"""
        return self.audio
    
    def getClipboardMode(self):
        """Return the clipboardmode attribute of this L{pyvb.vm.vbVM} instance.
        @return: The clipboardmode attribute.
        @rtype: String"""
        return self.clipboardmode
    
    def getSharedFolders(self):
        """Return the sharedfolders attribute of this L{pyvb.vm.vbVM} instance.
        @return: The sharedfolders attribute.
        @rtype: String"""
        cmd='%s %s'%(VB_COMMAND_SHOWVMINFO, self.getUUID())
        command=VBCommand(command=cmd)
        parser=vbVmParser()
        command.run()
        result=parser._parseAdditional(command.read, VB_RE_NAME)
        parser=vbSharedFolderParser()
        return parser.parse(result)
    
    def getHDD(self):
        """Return the uuid of this machin's HDD.
        @return: The uuid of the HDD.
        @rtype: String"""
        uuid=vbVmParser().parseHddUUID(self.getPrimaryMaster())
        parser=vbHddParser()
        cmd='%s %s'%(VB_COMMAND_SHOWVDIINFO, uuid)
        command=VBCommand(command=cmd)
        command.run()
        return parser.parseSingle(command.read)[0]
    
    def getStateName(self):
        """Return the state name of this virtual machine's state.
        @return: The state name.
        @rtype: String"""
        return self.getState().getName()