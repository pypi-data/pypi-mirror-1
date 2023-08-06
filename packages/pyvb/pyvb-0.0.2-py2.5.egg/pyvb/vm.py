"""
vm - pyvb module that holds the implementation of all VM related abstractions.
"""
from pyvb.constants import *
from pyvb.parser import *

class vbVmParser(vbParser):
    def __init__(self):
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
        vms=[]
        for result in self._parse(file):
            found_vm=vbVM(name=result['name'],\
                          guestos=result['guestos'],\
                          uuid=result['uuid'],\
                          configfile=result['configfile'],\
                          memorysize=result['memorysize'],\
                          vramsize=result['vramsize'],\
                          bootmenumode=result['bootmenumode'],\
                          acpi=result['acpi'],\
                          ioacpi=result['ioacpi'],\
                          timeoffset=result['timeoffset'],\
                          virtext=result['virtext'],\
                          state=result['state'],\
                          monitorcount=result['monitorcount'],\
                          floppy=result['floppy'],\
                          primarymaster=result['primarymaster'],\
                          dvd=result['dvd'],\
                          nic1=result['nic1'],\
                          nic2=result['nic2'],\
                          nic3=result['nic3'],\
                          nic4=result['nic4'],\
                          uart1=result['uart1'],\
                          uart2=result['uart2'],\
                          audio=result['audio'],\
                          clipboardmode=result['clipboardmode'],\
                          sharedfolders=result['sharedfolders'])
            vms.append(found_vm)
        return vms
    
    def parseHddUUID(self, hdd):
        return VB_RE_UUID2.match(hdd).groups()[1]
    
class vbVM:
    def __init__(self, **kw):
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
        self.name=name
        
    def setGuestos(self, guestos):
        self.guestos=guestos
        
    def setUUID(self, uuid):
        self.uuid=uuid
        
    def setConfigfile(self, configfile):
        self.configfile=configfile
        
    def setMemorysize(self, memorysize):
        self.memorysize=memorysize
        
    def setVramsize(self, vramsize):
        self.vramsize=vramsize
        
    def setBootmenumode(self, bootmenumode):
        self.bootmenumode=bootmenumode
        
    def setACPI(self, acpi):
        self.acpi=acpi
        
    def setIOACPI(self, ioacpi):
        self.ioacpi=ioacpi
        
    def setTimeoffset(self, timeoffset):
        self.timeoffset=timeoffset
        
    def setVirtext(self, virtext):
        self.virtext=virtext
        
    def setState(self, state):
        self.state=state
        
    def setMonitorcount(self, monitorcount):
        self.monitorcount=monitorcount
        
    def setFloppy(self, floppy):
        self.floppy=floppy
        
    def setPrimarymaster(self, primarymaster):
        self.primarymaster=primarymaster
        
    def setDVD(self, dvd):
        self.dvd=dvd
        
    def setNIC1(self, nic1):
        self.nic1=nic1
        
    def setNIC2(self, nic2):
        self.nic2=nic2
        
    def setNIC3(self, nic3):
        self.nic3=nic3
        
    def setNIC4(self, nic4):
        self.nic4=nic4
        
    def setUART1(self, uart1):
        self.uart1=uart1
        
    def setUART2(self, uart2):
        self.uart2=uart2
        
    def setAudio(self, audio):
        self.audio=audio
        
    def setClipboardmode(self, clipboardmode):
        self.clipboardmode=clipboardmode
        
    def setSharedfolders(self, sharedfolders):
        self.sharedfolders=sharedfolders
        
    def getName(self):
        return self.name
    
    def getGuestos(self):
        return self.guestos
    
    def getUUID(self):
        return self.uuid
    
    def getConfigfile(self):
        return self.configfile
    
    def getMemorysize(self):
        return self.memorysize
    
    def getVramsize(self):
        return self.vramsize
    
    def getBootmenumode(self):
        return self.bootmenumode
    
    def getACPI(self):
        return self.acpi
    
    def getIOACPI(self):
        return self.ioacpi
    
    def getTimeoffset(self):
        return self.timeoffset
    
    def getVirtext(self):
        return self.virtext
    
    def getState(self):
        return self.state
    
    def getMonitorcount(self):
        return self.monitorcount
    
    def getFloppy(self):
        return self.floppy
    
    def getPrimarymaster(self):
        return self.primarymaster
    
    def getDVD(self):
        return self.dvd
    
    def getNIC1(self):
        return self.nic1
    
    def getNIC2(self):
        return self.nic2
    
    def getNIC3(self):
        return self.nic3
    
    def getNIC4(self):
        return self.nic4
    
    def getUART1(self):
        return self.uart1
    
    def getUART2(self):
        return self.uart2
    
    def getAudio(self):
        return self.audio
    
    def getClipboardmode(self):
        return self.clipboardmode
    
    def getSharedfolders(self):
        return self.sharedfolders
    
    def getHDD(self):
        return vbVmParser().parseHddUUID(self.getPrimarymaster())