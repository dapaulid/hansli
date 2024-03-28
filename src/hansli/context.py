from . import utils

class Context(utils.Persistent):
	def __init__(self, name):
		super().__init__(name)
		self.messages = []
		self.tokens_input = 0
		self.tokens_output = 0
		self.tokens_total = 0	
		#self.load()
	# end functions
# end class