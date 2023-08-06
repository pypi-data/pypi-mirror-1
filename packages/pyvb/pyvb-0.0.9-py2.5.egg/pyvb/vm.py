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
                found_vm.setGuestos(result['guestos'])
            except KeyError:
                pass
            try:
                found_vm.setUUID(result['uuid'])
            except KeyError:
                pass
            try:
                found_vm.setConfigfile(result['configfile'])
            except KeyError:
                pass
            try:
                found_vm.setMemorysize(result['memorysize'])
            except KeyError:
                pass
            try:
                found_vm.setVramsize(result['vramsize'])
            except KeyError:
                pass
            try:
                found_vm.setBootmenumode(result['bootmenumode'])
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
                found_vm.setTimeoffset(result['timeoffset'])
            except KeyError:
                pass
            try:
                found_vm.setVirtext(result['virtext'])
            except KeyError:
                pass
            try:
                found_vm.setState(result['state'])
            except KeyError:
                pass
            try:
                found_vm.setMonitorcount(result['monitorcount'])
            except KeyError:
                pass
            try:
                found_vm.setFloppy(result['floppy'])
            except KeyError:
                pass
            try:
                found_vm.setPrimarymaster(result['primarymaster'])
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
                found_vm.setClipboardmode(result['clipboardmode'])
            except KeyError:
                pass
            try:
                found_vm.setSharedfolders(result['sharedfolders'])
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
            self.setGuestos(kw['guestos'])
        except KeyError:
            self.setGuestos('')
        try:
            self.setUUID(kw['uuid'])
        except KeyError:
            self.setUUID('')
        try:
            self.setConfigfile(kw['configfile'])
        except KeyError:
            self.setConfigfile('')
        try:
            self.setMemorysize(kw['memorysize'])
        except KeyError:
            self.setMemorysize('')
        try:
            self.setVramsize(kw['vramsize'])
        except Exception, e:
            self.setVramsize('')
        try:
            self.setBootmenumode(kw['bootmenumode'])
        except KeyError:
            self.setBootmenumode('')
        try:
            self.setACPI(kw['acpi'])
        except KeyError:
            self.setACPI('')
        try:
            self.setIOACPI(kw['ioacpi'])
        except KeyError:
            self.setIOACPI('')
        try:
            self.setTimeoffset(kw['timeoffset'])
        except KeyError:
            self.setTimeoffset('')
        try:
            self.setVirtext(kw['virtext'])
        except KeyError:
            self.setVirtext('')
        try:
            self.setState(kw['state'])
        except KeyError:
            self.setState('')
        try:
            self.setMonitorcount(kw['monitorcount'])
        except KeyError:
            self.setMonitorcount('')
        try:
            self.setFloppy(kw['floppy'])
        except KeyError:
            self.setFloppy('')
        try:
            self.setPrimarymaster(kw['primarymaster'])
        except KeyError:
            self.setPrimarymaster('')
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
            self.setClipboardmode(kw['clipboardmode'])
        except KeyError:
            self.setClipboardmode('')
        try:
            self.setSharedfolders(kw['sharedfolders'])
        except KeyError:
            self.setSharedfolders('')     
    
    def setName(self, name):
        """Set the name attribute of this L{pyvb.vm.vbVM} instance.
        @param name: The name attribute.
        @type name: String
        @return: None
        @rtype: None"""
        self.name=name
        
    def setGuestos(self, guestos):
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
        
    def setConfigfile(self, configfile):
        """Set the configfile attribute of this L{pyvb.vm.vbVM} instance.
        @param configfile: The configfile attribute.
        @type configfile: String
        @return: None
        @rtype: None"""
        self.configfile=configfile
        
    def setMemorysize(self, memorysize):
        """Set the memorysize attribute of this L{pyvb.vm.vbVM} instance.
        @param memorysize: The memorysize attribute.
        @type memorysize: String
        @return: None
        @rtype: None"""
        self.memorysize=memorysize
        
    def setVramsize(self, vramsize):
        """Set the vramsize attribute of this L{pyvb.vm.vbVM} instance.
        @param vramsize: The vramsize attribute.
        @type vramsize: String
        @return: None
        @rtype: None"""
        self.vramsize=vramsize
        
    def setBootmenumode(self, bootmenumode):
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
        
    def setTimeoffset(self, timeoffset):
        """Set the timeoffset attribute of this L{pyvb.vm.vbVM} instance.
        @param timeoffset: The timeoffset attribute.
        @type timeoffset: String
        @return: None
        @rtype: None"""
        self.timeoffset=timeoffset
        
    def setVirtext(self, virtext):
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
        
    def setMonitorcount(self, monitorcount):
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
        
    def setPrimarymaster(self, primarymaster):
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
        
    def setClipboardmode(self, clipboardmode):
        """Set the clipboardmode attribute of this L{pyvb.vm.vbVM} instance.
        @param clipboardmode: The clipboardmode attribute.
        @type clipboardmode: String
        @return: None
        @rtype: None"""
        self.clipboardmode=clipboardmode
        
    def setSharedfolders(self, sharedfolders):
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
    
    def getGuestos(self):
        """Return the guestos attribute of this L{pyvb.vm.vbVM} instance.
        @return: The guestos attribute.
        @rtype: String"""
        return self.guestos
    
    def getUUID(self):
        """Return the uuid attribute of this L{pyvb.vm.vbVM} instance.
        @return: The uuid attribute.
        @rtype: String"""
        return self.uuid
    
    def getConfigfile(self):
        """Return the configfile attribute of this L{pyvb.vm.vbVM} instance.
        @return: The configfile attribute.
        @rtype: String"""
        return self.configfile
    
    def getMemorysize(self):
        """Return the memorysize attribute of this L{pyvb.vm.vbVM} instance.
        @return: The memorysize attribute.
        @rtype: String"""
        return self.memorysize
    
    def getVramsize(self):
        """Return the vramsize attribute of this L{pyvb.vm.vbVM} instance.
        @return: The vramsize attribute.
        @rtype: String"""
        return self.vramsize
    
    def getBootmenumode(self):
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
    
    def getTimeoffset(self):
        """Return the timeoffset attribute of this L{pyvb.vm.vbVM} instance.
        @return: The timeoffset attribute.
        @rtype: String"""
        return self.timeoffset
    
    def getVirtext(self):
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
    
    def getMonitorcount(self):
        """Return the monitorcount attribute of this L{pyvb.vm.vbVM} instance.
        @return: The monitorcount attribute.
        @rtype: String"""
        return self.monitorcount
    
    def getFloppy(self):
        """Return the floppy attribute of this L{pyvb.vm.vbVM} instance.
        @return: The floppy attribute.
        @rtype: String"""
        return self.floppy
    
    def getPrimarymaster(self):
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
    
    def getClipboardmode(self):
        """Return the clipboardmode attribute of this L{pyvb.vm.vbVM} instance.
        @return: The clipboardmode attribute.
        @rtype: String"""
        return self.clipboardmode
    
    def getSharedfolders(self):
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
        uuid=vbVmParser().parseHddUUID(self.getPrimarymaster())
        parser=vbHddParser()
        cmd='%s %s'%(VB_COMMAND_SHOWVDIINFO, uuid)
        command=VBCommand(command=cmd)
        command.run()
        return parser.parseSingle(command.read)[0]
    
    def getStateName(self):
        return self.getState().getName()