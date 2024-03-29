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
from .. import utils
from ..utils import Failed

import importlib

#-------------------------------------------------------------------------------
# class definition
#-------------------------------------------------------------------------------
#
class LLM:

	def __init__(self, name, model):
		self.name = name
		self.model = model
	# end function

	def add_prepromt(self, msg):
		utils.abstract()

	def chat(self, msg):
		utils.abstract()

	@staticmethod
	def create(name, model):
		# derive module name from model name
		api = LLM.split_model(model)[1]
		api_suffix = api.split('.')[0]
		# import module
		mod = importlib.import_module('.llm_%s' % api_suffix, __package__)
		# create subclass
		llm = mod.create(name, model)
		# load preprompt from file
		preprompt = utils.load_file(utils.from_here('preprompts/' + name + '.md'))
		llm.add_prepromt(preprompt)
		# done
		return llm
	# end function

	@staticmethod
	def split_model(model):
		s = model.split('@')
		if len(s) != 2:
			raise Failed("invalid LLM identifier: '%s', must be of form 'modelname@provider.org'" % model)
		return s
	# end function

# end class


#-------------------------------------------------------------------------------
# end of file

