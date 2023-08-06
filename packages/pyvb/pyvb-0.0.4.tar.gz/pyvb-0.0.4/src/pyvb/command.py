"""
command - pyvb module that holds a simple command abstraction
used to run VirtualBox commands.
"""
import popen2
from pyvb.exception import vbCommandError

class VBCommand:
	def __init__(self, command=''):
		self.command=command
	
	def run(self):
		self.read, self.write, self.error=popen2.popen3(self.command)
		error_message=self.error.read()
		if error_message:
			raise vbCommandError(error_message)