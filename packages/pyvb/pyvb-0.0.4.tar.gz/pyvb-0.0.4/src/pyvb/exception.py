"""exception - Custom pyvb exceptions."""

class vbBaseException(Exception):
	def __init__(self, msg):
		Exception.__init__(self, msg)
		
class vbCommandError(vbBaseException):
	def __init__(self, msg):
		vbBaseException.__init__(self, msg)
		
class vbDvdError(vbBaseException):
	def __init__(self, msg):
		vbBaseException.__init__(self, msg)
		
class vbHddError(vbBaseException):
	def __init__(self, msg):
		vbBaseException.__init__(self, msg)
		
class vbOsTypeError(vbBaseException):
	def __init__(self, msg):
		vbBaseException.__init__(self, msg)
		
class vbParserError(vbBaseException):
	def __init__(self, msg):
		vbBaseException.__init__(self, msg)
		
class vbVmError(vbBaseException):
	def __init__(self, msg):
		vbBaseException.__init__(self, msg)