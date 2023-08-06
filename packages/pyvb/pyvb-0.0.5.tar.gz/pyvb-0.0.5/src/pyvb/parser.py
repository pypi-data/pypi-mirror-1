"""
parser - pyvb module that holds the implementation of the base parser
used to parse the VirtualBox command line output.
"""
class vbParser:
	def __init__(self):
		pass
	
	def _parse(self, file):
		parse_results=[]
		for line in file.readlines():
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