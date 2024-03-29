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

import yaml

from .report import Report
from . import utils
from .utils import Failed

#-------------------------------------------------------------------------------
# class definition
#-------------------------------------------------------------------------------
#
class Executor:
	def __init__(self, config_file):
		self.config = utils.load_file(config_file)
	# end function

	def execute(self, command, input, report: Report):
		cmd = self.config['commands'].get(command)
		if not cmd:
			raise Failed("the given command is unknown: %s" % command)
		
		# run dependencies if any
		requires = cmd.get('requires')
		if requires:
			success, input = self.execute(requires, input, report)
			if not success:
				return False, None
			# end if
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
		report.append_file(shell_file, label="%s command" % command)
		ret = subprocess.run('./' + os.path.basename(shell_file), 
			shell=True, cwd=dirname, 
			stdout=subprocess.PIPE, stderr=subprocess.STDOUT)	
		stdout = ret.stdout.decode()
		report.append_block(stdout, title="%s output" % command, lang='sh')
		success = ret.returncode == 0
		# provide more context on failure
		if not success:
			report.append_file(input, label="%s input" % command)
		return success, output
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

