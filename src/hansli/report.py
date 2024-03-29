#-------------------------------------------------------------------------------
#
#	@license
#	Copyright (c) Daniel Pauli <dapaulid@gmail.com>
#
#	This source code is licensed under the MIT license found in the
#	LICENSE file in the root directory of this source tree.
#
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
# imports 
#-------------------------------------------------------------------------------
#
from . import utils
from .utils import Failed

#-------------------------------------------------------------------------------
# class definition
#-------------------------------------------------------------------------------
#
class Report:
	def __init__(self):
		self.markdown = ""
	# end function

	def append_block(self, content, title=None, lang=None):
		self.markdown += "# %s\n```%s\n%s```\n" % (title, lang, content)
	# end function		

	def append_file(self, filename, label=None):
		with open(filename, 'r') as inp:
			content = inp.read()
		title = filename
		if label:
			title = label + ": " + title
		self.append_block(content, title=title, lang=utils.file_ext(filename)[1:])	
	# end function

# end class


#-------------------------------------------------------------------------------
# end of file

