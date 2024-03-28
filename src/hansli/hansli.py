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
	parser.add_argument('sourcefile',
		help="the source file of the program to run")
	parser.add_argument('args', nargs='*', 
		help="program arguments")
	# that's all   
	args = parser.parse_args()

	# do it
	run(args)
# end function

#-------------------------------------------------------------------------------
# functions
#-------------------------------------------------------------------------------
#
def run(args):
	llm = LLM_OpenAI("autofix", "gpt-3.5-turbo")	
	report = report_file(args.sourcefile)
	max_attempts = 3
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
def write_sh(filename, content):
	with open(filename, 'w') as out:
		out.write(content + '\n')
	os.chmod(filename, 0o744)
# end function

#-------------------------------------------------------------------------------
#
def entry():
	try:
		main()
	except Failed as e:
		error_console.print("error: %s" % e)
	# end try
# end function	
		
#-------------------------------------------------------------------------------
# end of file