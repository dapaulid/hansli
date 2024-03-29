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

from rich.console import Console
from rich.markdown import Markdown

from .executor import Executor
from .report import Report
from . import utils
from .utils import prog, Failed

from .llm_openai import LLM_OpenAI

console = Console()
error_console = Console(stderr=True, style="bold red")

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
	parser.add_argument('command',
		help="command to execute, e.g. run or build")
	parser.add_argument('input',
		help="path to the input file or directory")
	parser.add_argument('args', nargs='*', 
		help="program arguments")
	# that's all   
	args = parser.parse_args()

	executor = Executor(utils.from_here("config/executor.yml"))

	attempts = 0
	max_attempts = 3
	while True:
		report = Report() # TODO keep state over retries?
		success, output = executor.execute(args.command, args.input, report)
		console.print(Markdown(report.markdown))
		if success:
			break
		else:
			if attempts < max_attempts:
				attempts += 1
				autofix(args.input, report)
			else:
				raise Failed("autofix did not succeed after %d attempts" % max_attempts)
			# end if
		# # end if
	if attempts == 0:
		print("success!")
	else:
		print("success after %d autofix attempts" % attempts)

	return

	# do it
	run(args)
# end function

#-------------------------------------------------------------------------------
#
def autofix(input, report: Report):
	llm = LLM_OpenAI("autofix", "gpt-3.5-turbo")
	reply = llm.chat(report.markdown)
	console.print(Markdown(reply))
	lang = os.path.splitext(input)[1][1:]
	code = utils.extract_code_block(reply, lang)
	if not code:
		raise Failed("AI did not correctly generate source code")
	utils.save_file(input, code)	
# end function	

#-------------------------------------------------------------------------------
# functions
#-------------------------------------------------------------------------------
#
def run(args):
	llm = LLM_OpenAI("autofix", "gpt-3.5-turbo")	
	report = report_file(args.sourcefile)
	max_attempts = 0
	i = 0
	while True:
		try:
			build(args, report)
			break
		except subprocess.CalledProcessError as e:
			report += "# build output\n```sh\n%s```\n" % e.output.decode()
			console.print(Markdown(report))
			if i < max_attempts:
				i += 1
				reply = llm.chat(report)
				report = ""
				console.print(Markdown(reply))
				lang = os.path.splitext(args.sourcefile)[1][1:]
				code = utils.extract_code_block(reply, lang)
				if not code:
					raise Failed("AI did not correctly generate source code")
				utils.save_file(args.sourcefile, code)
			else:
				raise Failed("autofix did not succeed after %d attempts" % max_attempts)
		# end try 
	# end while
	

	executable = os.path.splitext(args.sourcefile)[0]
	subprocess.check_call([executable] + args.args)

# end function

#-------------------------------------------------------------------------------
#	
def build(args, report):
	dirname = os.path.dirname(args.sourcefile)
	basename = os.path.basename(args.sourcefile)
	[noext, ext] = os.path.splitext(basename)
	build_file = os.path.join(dirname, "build-%s.sh" % noext)
	# generate build file if necessary
	if not os.path.exists(build_file):
		if ext in ['.cpp']:
			write_sh(build_file, "g++ %s -o %s" % (basename, noext)) 
		else:
			raise Failed("unsupported file type: %s" % ext)
		# end if
	# end if
	report += report_file(build_file)
	subprocess.check_output('./' + os.path.basename(build_file), shell=True, cwd=dirname, stderr=subprocess.STDOUT)
# end function

def report_file(filename):
	with open(filename, 'r') as inp:
		content = inp.read()
	return "# %s\n```%s\n%s```\n" % (filename, os.path.splitext(filename)[1][1:], content)
# end function

def generate_report(source_file, build_file, build_output):
	report = report_file(source_file)
	report += report_file(build_file)
	report += "# build output\n```sh\n%s```\n" % build_output
	return report
# end function

#-------------------------------------------------------------------------------
#
import traceback
def entry():
	try:
		main()
	except Failed as e:
		error_console.print("[ERROR] %s" % e)
	except FileNotFoundError as e:
		error_console.print(traceback.format_exc().strip())
		error_console.print("  cwd: %s\n" % os.getcwd())
	except:
		error_console.print(traceback.format_exc())		
	# end try
# end function	
		
#-------------------------------------------------------------------------------
# end of file