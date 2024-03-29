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
import argparse
import os
import subprocess
import sys
import traceback

from .executor import Executor
from .report import Report
from . import utils
from .utils import prog, Failed
from .config import config

from .llm import LLM

#-------------------------------------------------------------------------------
# constants
#-------------------------------------------------------------------------------
#

# usage examples shown at end of help description
USAGE_EXAMPLES = """
"""

#-------------------------------------------------------------------------------
# main
#-------------------------------------------------------------------------------
#
def main():
	# parse command line
	parser = argparse.ArgumentParser(
		description="%s v%s - %s\n  %s" % (prog.name, prog.version, prog.description, prog.website),
		epilog="examples:" + USAGE_EXAMPLES,
		formatter_class=argparse.RawTextHelpFormatter)
	parser.add_argument('command', nargs='?',
		help="command to execute, e.g. run or build")
	parser.add_argument('input', nargs='?',
		help="path to the input file or directory")
	parser.add_argument('args', nargs='*', 
		help="program arguments")

	# that's all   
	args = parser.parse_args()

	# handle API key management
	# TODO use subparser for this? The problem is that we need some kind of "default subparser"
	# so that command/input still works without specifying a subcommand
	if args.command == 'apikey':
		name = args.input
		value = args.args[0] if len(args.args) > 0 else None
		if not name:
			raise Failed("please specify name of API key to set/clear")
		config.set_apikey(name, value)
		return
	# end if

	# do it
	execute(args)

# end function

#-------------------------------------------------------------------------------
# functions
#-------------------------------------------------------------------------------
#
def execute(args):
	
	executor = Executor(utils.from_here("config/executor.yml"))

	attempts = 0
	max_attempts = 3
	while True:
		report = Report() # TODO keep state over retries?
		success, output = executor.execute(args.command, args.input, report)
		utils.print_markdown(report.markdown)
		if success:
			break
		else:
			if attempts < max_attempts:
				attempts += 1
				autofix(args.input, report)
			else:
				raise Failed("autofix did not succeed after %d attempts" % max_attempts)
			# end if
		# end if
	# end while
	if attempts == 0:
		print("success!")
	else:
		print("success after %d autofix attempts" % attempts)
	# end if
# end function

#-------------------------------------------------------------------------------
#
def autofix(input, report: Report):
	llm = LLM.create("autofix", "gpt-3.5-turbo@openai.com")
	reply = llm.chat(report.markdown)
	utils.print_markdown(reply)
	lang = os.path.splitext(input)[1][1:]
	code = utils.extract_code_block(reply, lang)
	if not code:
		raise Failed("AI did not correctly generate source code")
	utils.save_file(input, code)	
# end function	

#-------------------------------------------------------------------------------
#
def entry():
	try:
		main()
	except Failed as e:
		utils.error(e)
	except FileNotFoundError as e:
		utils.error_console.print(traceback.format_exc().strip())
		utils.error_console.print("  cwd: %s\n" % os.getcwd())
	except Exception:
		utils.error_console.print(traceback.format_exc())
	# end try
# end function	
		
#-------------------------------------------------------------------------------
# end of file