from rich.console import Console
from rich.markdown import Markdown

from hansli.llm.llm_openai import LLM_OpenAI

console = Console()

#llm = LLM_OpenAI("mychat", "gpt-4-turbo-preview")
llm = LLM_OpenAI("mychat", "gpt-3.5-turbo")

for msg in llm.ctx.messages:
	if msg['role'] == 'user':
		prefix = "**>>** "
	elif msg['role'] == 'assistant':
		prefix = ""
	else:
		prefix = "**[%s]** " % msg['role']
	# end if
	console.print(Markdown(prefix + msg['content']))

while True:
	user_input = console.input(">> ")
	if not user_input:
		break
	reply = Markdown(llm.chat(user_input))
	console.print(reply)
# end while
