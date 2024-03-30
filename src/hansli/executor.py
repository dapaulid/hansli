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
import os
import subprocess
import sys

import yaml

from .report import Report
from . import utils
from .utils import Failed

#-------------------------------------------------------------------------------
# class definition
#-------------------------------------------------------------------------------
#
class Executor:
	def __init__(self, config_file, verbose=False):
		self.config = utils.load_file(config_file)
		self.verbose = verbose
	# end function

	def execute(self, command, input, report=None, depth=0):
		cmd = self.config['commands'].get(command)
		if not cmd:
			raise Failed("the given command is unknown: %s" % command)
		
		# run dependencies if any
		requires = cmd.get('requires')
		if requires:
			input = self.execute(requires, input, report, depth+1)
		# end if

		dirname = os.path.dirname(input)
		input_rel = os.path.basename(input)
		[input_rel_noext, ext] = os.path.splitext(input_rel)
		output_rel = input_rel_noext
		output = os.path.join(dirname, output_rel)
		shell_file = os.path.join(dirname, "%s-%s.sh" % (command, input_rel_noext))
		# create shell file if not existing
		if not os.path.exists(shell_file):
			placeholders = {
				'input': input_rel,
				'output': output_rel,
			}
			shell_cmd = cmd['shell'] % placeholders
			write_sh(shell_file, shell_cmd)
		# execute it
		if report:
			report.append_file(shell_file, label="%s command" % command)

		# only show output of first command, unless verbose mode is enabled
		print_all_output = depth == 0 or self.verbose
		# we need to capture output if a report is requested
		# or we do not print the output directly (so that we can output it after errors)
		capture = report is not None or not print_all_output
		if capture:
			stdout = subprocess.PIPE
			stderr = subprocess.STDOUT
		else:
			stdout = None
			stderr = None
		# end if

		# start process
		proc = subprocess.Popen('./' + os.path.basename(shell_file), 
			shell=True, cwd=dirname, stdout=stdout, stderr=stderr)

		if capture:
			captured_output = ""
			while True:
				line = proc.stdout.readline().decode()
				if not line: break
				if print_all_output:
					#utils.console.print(line, end=None)
					sys.stdout.write(line)
				captured_output += line
			# end while
		# end if
		returncode = proc.wait()
		success = returncode == 0

		if capture:
			captured_output += proc.stdout.read().decode()			

		if report:
			report.append_block(captured_output, title="%s output" % command, lang='sh')
			# provide more context on failure
			#if not success:
			try:
				report.append_file(input, label="%s input" % command)
			except UnicodeDecodeError:
				# probably a binary file
				pass
			# end try				
		# end if

		# handle error
		if not success:
			if capture:
				sys.stdout.write(captured_output)

			raise Failed("%s failed with errors. Try again with '--autofix' to correct them automatically." % command)

		# success
		return output
	# end function
# end class

#-------------------------------------------------------------------------------
# helpers
#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
#
def write_sh(filename, content):
	with open(filename, 'w') as out:
		out.write(content + '\n')
	os.chmod(filename, 0o744)
# end function


#-------------------------------------------------------------------------------
# end of file

