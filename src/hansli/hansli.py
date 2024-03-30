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

	parser.add_argument('-a', '--autofix', action='store_true',
		help="attempt to fix errors automatically")
	parser.add_argument('--autoimprove', action='store_true',
		help="let an AI assistant improve the input files")
	parser.add_argument('-v', '--verbose', action='store_true',
		help="print all subprocess output")

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
	
	executor = Executor(utils.from_here("config/executor.yml"), 
		verbose=args.verbose)

	if args.autofix:
		# with autofix
		attempts = 0
		max_attempts = 1
		while True:
			report = Report() # TODO keep state over retries?
			try:
				executor.execute(args.command, args.input, report)
				break
			except Failed:
				if attempts < max_attempts:
					attempts += 1
					autofix(report)
				else:
					raise Failed("autofix did not succeed after %d attempts" % max_attempts)
				# end if
			# try
		# end while
		if attempts == 0:
			print("success!")
		else:
			print("success after %d autofix attempts" % attempts)
		# end if
	elif args.autoimprove:
		# with autoimprove
		report = Report()
		executor.execute(args.command, args.input, report)
		autoimprove(report)
	else:
		# the boring way
		executor.execute(args.command, args.input)
	# end if
# end function

#-------------------------------------------------------------------------------
#
def autofix(report: Report):
	llm = LLM.create("autofix", "gpt-3.5-turbo@openai.com")
	utils.print_markdown(report.markdown)	
	reply = llm.chat(report.markdown)
	utils.print_markdown(reply)
	corrected_files = utils.extract_code_blocks(reply, "Corrected file")
	if not corrected_files:
		print(reply)
		raise Failed("AI did not correctly generate source code")
	for filename, content in corrected_files:
		utils.save_file(filename, content)	
# end function

#-------------------------------------------------------------------------------
#
def autoimprove(report: Report):
	llm = LLM.create("autoimprove", "gpt-3.5-turbo@openai.com")
	utils.print_markdown(report.markdown)	
	reply = llm.chat(report.markdown)
	utils.print_markdown(reply)
	improved_files = utils.extract_code_blocks(reply, "Improved file")
	if len(improved_files) > 0:
		print("Your AI assistant improved the following files:")
		for filename, content in improved_files:
			print("  %s" % filename)
			utils.save_file(filename, content)	
		# end for
	else:
		print("Your AI assistant found nothing to improve")
	# end if
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