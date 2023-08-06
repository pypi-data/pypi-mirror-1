"""exception - Custom pyvb exceptions."""

class vbBaseException(Exception):
	"""The base exception that is inherited from all other pyvb exceptions."""
	def __init__(self, msg):
		"""Constructor.  Initilize the exception message.
		@param msg: The exception message.
		@type msg: String
		@return: A new L{pyvb.exception.vbBaseException} instance.
		@rtype: L{pyvb.exception.vbBaseException}"""
		Exception.__init__(self, msg)
		
class vbCommandError(vbBaseException):
	"""An exception that is raised when there is an error with a command."""
	def __init__(self, msg):
		"""Constructor.  Initialize the exception message.
		@param msg: The exception message.
		@type msg: String
		@return: A new L{pyvb.exception.vbCommandError} instance.
		@rtype: L{pyvb.exception.vbCommandError}"""
		vbBaseException.__init__(self, msg)
		
class vbDvdError(vbBaseException):
	"""An exception that is raised when there is an error with a DVD."""
	def __init__(self, msg):
		"""Constructor.  Initialize the exception message.
		@param msg: The exception message.
		@type msg: String
		@return: A new L{pyvb.exception.vbDvdError} instance.
		@rtype: L{pyvb.exception.vbDvdError}"""
		vbBaseException.__init__(self, msg)
		
class vbHddError(vbBaseException):
	"""An exception that is raised when there is an error with an HDD."""
	def __init__(self, msg):
		"""Constructor.  Initialize the exception message.
		@param msg: The exception message.
		@type msg: String
		@return: A new L{pyvb.exception.vbHddError} instance.
		@rtype: L{pyvb.exception.vbHddError}"""
		vbBaseException.__init__(self, msg)
		
class vbOsTypeError(vbBaseException):
	"""An exception that is raised when there is an error with an OS type."""
	def __init__(self, msg):
		"""Constructor.  Initialize the exception message.
		@param msg: The exception message.
		@type msg: String
		@return: A new L{pyvb.exception.vbOsTypeError} instance.
		@rtype: L{pyvb.exception.vbOsTypeError}"""
		vbBaseException.__init__(self, msg)
		
class vbParserError(vbBaseException):
	"""An exception that is raised when there is an error with a parser."""
	def __init__(self, msg):
		"""Constructor.  Initialize the exception message.
		@param msg: The exception message.
		@type msg: String
		@return: A new L{pyvb.exception.vbParserError} instance.
		@rtype: L{pyvb.exception.vbParserError}"""
		vbBaseException.__init__(self, msg)
		
class vbVmError(vbBaseException):
	"""An exception that is raised when there is an error with a vm."""
	def __init__(self, msg):
		"""Constructor.  Initialize the exception message.
		@param msg: The exception message.
		@type msg: String
		@return: A new L{pyvb.exception.vbVmError} instance.
		@rtype: L{pyvb.exception.vbVmError}"""
		vbBaseException.__init__(self, msg)
		
class vbVmNotFound(vbBaseException):
	"""An exception that is raised when there is a vm cannot be found."""
	def __init__(self, msg):
		"""Constructor.  Initialize the exception message.
		@param msg: The exception message.
		@type msg: String
		@return: A new L{pyvb.exception.vbVmNotFound} instance.
		@rtype: L{pyvb.exception.vbVmNotFound}"""
		vbBaseException.__init__(self, msg)