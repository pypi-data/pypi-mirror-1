"""
vb - pyvb module that holds the implementaton of the VB class
that is meant to be instantiated as a singleton.
"""
from pyvb.constants import *
from pyvb.command import *
from pyvb.vm import *
from pyvb.ostype import *
from pyvb.dvd import *
from pyvb.hdd import *
from pyvb.exception import *

class VB:
	"""This class is meant to be an abstraction of the VirtualBox appliacation.
	So there should really only be one instance of this class although there
	is nothing preventing it from being instantiated multiple times."""
	def __init__(self):
		"""Constructor.  Does nothing at this point."""
		pass
	
	def run(self, command):
		"""Run the specified command on the command line.
		@param command: The command to run.
		@type command: L{pyvb.command.VBCommand}
		@return: The command object that was run.
		@rtype: L{pyvb.command.VBCommand}"""
		command.run()
		return command
	
	def listVMS(self, uuid=None):
		"""Return a list of VirtualBox virtual machines.  First we check
		if a specific machine is being requested.  In this case, we fetch
		a single VM by altering the command that is run.  Even if a single
		VM is requested, a list is still returned so the interface will 
		remain unchanged.  If a specific machine is not requested, a list
		of all VMs is returned.
		@keyword uuid: The id of a machine to retrieve.
		@type uuid: String
		@return: A list of L{pyvb.vm.vbVM} instances.
		@rtype: List"""
		if uuid:
			cmd='%s %s'%(VB_COMMAND_SHOWVMINFO, uuid)
			command=VBCommand(command=cmd)
		else:
			command=VBCommand(command=VB_COMMAND_LIST_VMS)
		parser=vbVmParser()
		command.run()
		return parser.parse(command.read)
	
	def listOsTypes(self):
		"""Return a list of VitualBox-supported operating system types.
		@return: A list of L{pyvb.ostype.vbOsType} instances.
		@rtype: List"""
		command=VBCommand(command=VB_COMMAND_LIST_OSTYPES)
		parser=vbOsTypeParser()
		command.run()
		return parser.parse(command.read)
	
	def listHostDvds(self):
		"""Return a list of host DVDs.
		@return: A list of L{pyvb.dvd.vbHostDvd} instances.
		@rtype: List"""
		command=VBCommand(command=VB_COMMAND_LIST_HOSTDVDS)
		parser=vbHostDvdParser()
		command.run()
		return parser.parse(command.read)
	
	def listDvds(self):
		"""Return a list of DVDs used by virtual machines.
		@return: A list of L{pyvb.dvd.vbDvd} instances.
		@rtype: List"""
		command=VBCommand(command=VB_COMMAND_LIST_DVDS)
		parser=vbDvdParser()
		command.run()
		return parser.parse(command.read)
	
	def listHdds(self, uuid=None):
		"""Return a list of HDDs in use by VirtualBox.  First, we check
		if a specific HDD was requested.  In this case, we fetch a single
		HDD by altering the command that is run.  Even if a single HDD is
		requested, a list is still returned so the interface will remain 
		unchanged.  If a specific HDD is requested, a list of all HDDs is
		returned.
		@return: A list of L{pyvb.hdd.vbHdd} instances.
		@rtype: List"""
		parser=vbHddParser()
		if uuid:
			cmd='%s %s'%(VB_COMMAND_SHOWVDIINFO, uuid)
			command=VBCommand(command=cmd)
			command.run()
			return parser.parseSingle(command.read)
		else:
			command=VBCommand(command=VB_COMMAND_LIST_HDDS)
			command.run()
			return parser.parse(command.read)
	
	def getVM(self, uuid):
		"""Return a specific VirtualBox virtual machine using the specified id.
		@param uuid: The id of the machine to retrieve.
		@type uuid: String
		@return: The specified VirtualBox virtual machine.
		@rtype: L{pyvb.vm.vbVM}"""
		try:
			return self.listVMS(uuid)[0]
		except IndexError:
			raise vbVmNotFound('Virtual Machine %s could not be found.'%(uuid))
		
	def getHDD(self, uuid):
		"""Return a specific VirtualBox HDD using the specified id.
		@param uuid: The id of the HDD to retrieve.
		@type uuid: String
		@return: The specified VirtualBox HDD.
		@rtype: L{pyvb.hdd.vbHdd}"""
		try:
			return self.listHdds(uuid)[0]
		except IndexError:
			return
		
	def startVM(self, vm, type='gui'):
		"""Start the specified VirtualBox virtual machine.
		@param vm: The VM to start.
		@type vm: L{pyvb.vm.vbVM}"""
		cmd='%s %s -type %s'%(VB_COMMAND_STARTVM, vm.getUUID(), type)
		command=VBCommand(command=cmd)
		command.run()
		
	def poweroffVM(self, vm):
		"""Poweroff the specified VirtualBox virtual machine.
		@param vm: The VM to poweroff.
		@type vm: L{pyvb.vm.vbVM}"""
		cmd='%s %s %s'%(VB_COMMAND_CONTROLVM, vm.getUUID(), 'poweroff')
		command=VBCommand(command=cmd)
		command.run()
		
	def acpipoweroffVM(self, vm):
		"""ACPI poweroff the specified VirtualBox virtual machine.
		@param vm: The VM to poweroff.
		@type vm: L{pyvb.vm.vbVM}"""
		cmd='%s %s %s'%(VB_COMMAND_CONTROLVM, vm.getUUID(), 'acpipowerbutton')
		command=VBCommand(command=cmd)
		command.run()
		
	def pauseVM(self, vm):
		"""Pause the specified VirtualBox virtual machine.
		@param vm: The VM to pause.
		@type vm: L{pyvb.vm.vbVM}"""
		cmd='%s %s %s'%(VB_COMMAND_CONTROLVM, vm.getUUID(), 'pause')
		command=VBCommand(command=cmd)
		command.run()
		
	def resumeVM(self, vm):
		"""Resume the specified VirtualBox virtual machine.
		@param vm: The VM to resume.
		@type vm: L{pyvb.vm.vbVM}"""
		cmd='%s %s %s'%(VB_COMMAND_CONTROLVM, vm.getUUID(), 'resume')
		command=VBCommand(command=cmd)
		command.run()
		
	def createVM(self, name):
		"""Create a new virtual machine.
		@param name: The name of the new machine.
		@type name: String
		@return: A new L{pyvb.vm.vbVM} instance.
		@rtype: L{pyvb.vm.vbVM}"""
		cmd='%s -name "%s" -register'%(VB_COMMAND_CREATEVM, name)
		command=VBCommand(command=cmd)
		parser=vbVmParser()
		parser.attributes={'uuid':VB_RE_UUID}
		command.run()
		return parser.parse(command.read)[0]
	
	def createVDI(self, filename, size):
		"""Create a new disk-drive.
		@param filename: The location of the disk file.
		@type filename: String
		@param size: The size of the disk file in megabytes.
		@type size: Int
		@return: A new L{pyvb.hdd.vbHdd} instance.
		@rtype: L{pyvb.hdd.vbHdd}"""
		cmd='%s -filename "%s" -size "%s" -register'%(VB_COMMAND_CREATEVDI, filename, size)
		command=VBCommand(command=cmd)
		parser=vbHddParser()
		parser.attributes={'uuid':VB_RE_UUID3}
		command.run()
		return parser.parse(command.read)[0]
	
	def createDVD(self, filename):
		"""Create a new DVD.
		@param filename: The location of the ISO file.
		@type filename: String
		@return: A new L{pyvb.dvd.vbDvd} instance.
		@rtype: L{pyvb.dvd.vbDvd}"""
		cmd='%s dvd %s'%(VB_COMMAND_REGISTERIMAGE, filename)
		command=VBCommand(command=cmd)
		command.run()
		for dvd in self.listDvds():
			if filename==dvd.getPath():
				return dvd
			
	def attachVDI(self, vm, hdd):
		"""Attach a disk-drive to a virtual machine.
		@param vm: The virtual machine we are attaching the disk-drive to.
		@type vm: L{pyvb.vm.vbVM}
		@param hdd: The disk-drive we are attaching.
		@type hdd: L{pyvb.hdd.vbHdd}
		@return: None
		@rtype: None"""
		cmd='%s %s -hda %s'%(VB_COMMAND_MODIFYVM, vm.getUUID(), hdd.getUUID())
		command=VBCommand(command=cmd)
		command.run()
		
	def attachDVD(self, vm, dvd):
		"""Attach a DVD to a virtual machine.
		@param vm: The virtual machine we are attaching the DVD to.
		@type vm: L{pyvb.vm.vbVM}
		@param dvd: The DVD we are attaching.
		@type dvd: L{pyvb.dvd.vbDvd}
		@return: None
		@rtype: None"""
		cmd='%s %s -dvd %s'%(VB_COMMAND_MODIFYVM, vm.getUUID(), dvd.getUUID())
		command=VBCommand(command=cmd)
		command.run()