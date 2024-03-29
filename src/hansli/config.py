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
class Config(utils.Persistent):
	def __init__(self, name):
		super().__init__(name)
		self.api_keys = {}
		self.load()
	# end function
		
	def set_apikey(self, name, value):
		if value:
			self.api_keys[name] = value
		else:
			del self.api_keys[name]
	# end function	

# end class

# singleton
config = Config(utils.from_home('.hansli'))

#-------------------------------------------------------------------------------
# end of file

