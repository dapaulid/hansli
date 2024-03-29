from ..context import Context
from ..config import config
from .. import utils
from ..utils import Failed

from .llm import LLM

from openai import OpenAI

# factory function
def create(name, model):
	return LLM_OpenAI(name, model)

class LLM_OpenAI(LLM):
	def __init__(self, name, model):
		super().__init__(name, model)
		self.model_id = LLM.split_model(model)[0]
		# read API key from config
		api_key = config.api_keys.get('openai.com')
		if not api_key:
			raise Failed("please add API key for 'openai.com' to use model '%s'" % model)
		# init client
		self.client = OpenAI(
			api_key=api_key
		)
		self.ctx = Context(name)
	# end function
	
	def add_prepromt(self, msg):
		self.ctx.messages.append({ 'role': 'system', 'content': msg })

	def chat(self, msg):
		# add prompt to context
		self.ctx.messages.append({ 'role': 'user', 'content': msg })
		# call API
		completion = self.client.chat.completions.create(
			model=self.model_id,
			messages=self.ctx.messages
		)
		assert len(completion.choices) == 1
		# get reply
		reply = completion.choices[0].message
		# update context
		self.ctx.messages.append({ 'role': reply.role, 'content': reply.content })
		# update statistics
		self.ctx.tokens_input += completion.usage.prompt_tokens
		self.ctx.tokens_output += completion.usage.completion_tokens
		self.ctx.tokens_total += completion.usage.total_tokens
		# done
		return reply.content
	# end function

# end class


