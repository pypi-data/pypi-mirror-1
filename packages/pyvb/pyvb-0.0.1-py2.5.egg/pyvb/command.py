import popen2

class VBCommand:
	def __init__(self, command=''):
		self.command=command
	
	def run(self):
		self.read, self.write, self.error=popen2.popen3(self.command)