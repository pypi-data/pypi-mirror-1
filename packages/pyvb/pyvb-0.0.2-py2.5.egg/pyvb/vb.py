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

class VB:
	def __init__(self):
		pass
	
	def run(self, command):
		command.run()
		return command
	
	def listVMS(self, uuid=None):
		if uuid:
			cmd='%s %s'%(VB_COMMAND_SHOWVMINFO, uuid)
			command=VBCommand(command=cmd)
		else:
			command=VBCommand(command=VB_COMMAND_LIST_VMS)
		parser=vbVmParser()
		command.run()
		return parser.parse(command.read)
	
	def listOsTypes(self):
		command=VBCommand(command=VB_COMMAND_LIST_OSTYPES)
		parser=vbOsTypeParser()
		command.run()
		return parser.parse(command.read)
	
	def listHostDvds(self):
		command=VBCommand(command=VB_COMMAND_LIST_HOSTDVDS)
		parser=vbHostDvdParser()
		command.run()
		return parser.parse(command.read)
	
	def listDvds(self):
		command=VBCommand(command=VB_COMMAND_LIST_DVDS)
		parser=vbDvdParser()
		command.run()
		return parser.parse(command.read)
	
	def listHdds(self, uuid=None):
		if uuid:
			cmd='%s %s'%(VB_COMMAND_SHOWVDIINFO, uuid)
			command=VBCommand(command=cmd)
		else:
			command=VBCommand(command=VB_COMMAND_LIST_HDDS)
		parser=vbHddParser()
		command.run()
		return parser.parse(command.read)
	
	def getVM(self, uuid):
		try:
			return self.listVMS(uuid)[0]
		except IndexError:
			return
		
	def startVM(self, vm):
		cmd='%s %s'%(VB_COMMAND_STARTVM, vm.getUUID())
		command=VBCommand(command=cmd)
		command.run()
		
	def poweroffVM(self, vm):
		cmd='%s %s %s'%(VB_COMMAND_CONTROLVM, vm.getUUID(), 'poweroff')
		command=VBCommand(command=cmd)
		command.run()
		
	def acpipoweroffVM(self, vm):
		cmd='%s %s %s'%(VB_COMMAND_CONTROLVM, vm.getUUID(), 'acpipowerbutton')
		command=VBCommand(command=cmd)
		command.run()
		
	def pauseVM(self, vm):
		cmd='%s %s %s'%(VB_COMMAND_CONTROLVM, vm.getUUID(), 'pause')
		command=VBCommand(command=cmd)
		command.run()
		
	def resumeVM(self, vm):
		cmd='%s %s %s'%(VB_COMMAND_CONTROLVM, vm.getUUID(), 'resume')
		command=VBCommand(command=cmd)
		command.run()