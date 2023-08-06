"""
parser - pyvb module that holds the implementation of the base parser
used to parse the VirtualBox command line output.
"""

import types

class vbParser:
	"""The base pyvb parser used to construct Python abstractions of the
	VirtualBox command line output."""
	def __init__(self):
		"""Constructor.
		@return: A new L{pyvb.parser.vbParser} instance.
		@rtype: L{pyvb.parser.vbParser}"""
		pass
	
	def _parse(self, file):
		"""Construct a list of dictionaries based of the specified file.
		First we check if we are dealing with a file object of a list
		object.  We iterate through all the lines in the file.  If
		a list parameter was provided, a line is represented by a list
		element.  The inner loop is for the attributes in which we are
		searching.  We match against the attribute's regular expression
		and add it to the dictionary of found results.  The dictionary 
		represnting the current object is considered complete when the
		number of found attributes matches the number of attributes we
		are looking for.
		@param file: The file we are parsing.
		@type file: File/List
		@return: A list of parse results.
		@rtype: List"""
		parse_results=[]
		if type(file) is types.FileType:
			parse_input=file.readlines()
		elif type(file) is types.ListType:
			parse_input=file
		for line in parse_input:
			for attribute in self.attributes.keys():
				try:
					result=self.attributes[attribute].match(line).groups()[1]
					self.found_attributes[attribute]=result
				except AttributeError:
					pass
				if len(self.attributes)==len(self.found_attributes):
					parse_results.append(self.found_attributes)
					self.found_attributes={}
		return parse_results
	
	def _parseAdditional(self, file, expression):
		"""Parse the specified file for the specified expression
		and return the results excluding the first result found.
		@param file: The file we are parsing.
		@type file: File
		@param expression: The expression to match against.
		@type expression: Regex
		@return: A list of parse results.
		@rtype: List"""
		parse_results=[]
		first=False
		for line in file.readlines():
			try:
				result=expression.match(line).groups()[1]
				if first:
					parse_results.append(result)
				else:
					first=True
			except AttributeError,e:
				pass
		return parse_results
	
	def addAttribute(self, name, expression):
		self.attributes[name]=expression
		
	def removeAttribute(self, name):
		del self.attributes[name]