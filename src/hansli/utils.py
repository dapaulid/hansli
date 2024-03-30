#-------------------------------------------------------------------------------
#
#	Measures execution time of Python functions using decorators.
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
import atexit
import collections
import glob
import os
import re
import signal
import sys

from time import perf_counter as timer
from importlib.metadata import metadata

import yaml

from rich.console import Console
from rich.markdown import Markdown

console = Console()
error_console = Console(stderr=True)

#-------------------------------------------------------------------------------
# classes
#-------------------------------------------------------------------------------
#

#-------------------------------------------------------------------------------
#
# the most important metadata of the program
ProgInfo = collections.namedtuple('ProgInfo', 
    ['name', 'version', 'description', 'website', 'bugtracker']
)

#-------------------------------------------------------------------------------
#
class Failed(Exception):
    def __init__(self, message):
        super().__init__(message)
# end class

#-------------------------------------------------------------------------------
#
class OsPaths:
	if os.name == 'nt':
		APPDATA = os.getenv('APPDATA')
	else:
		APPDATA = os.path.expanduser('~/.local/share')
	# end if
# end class

#-------------------------------------------------------------------------------
#
class Persistent:
	def __init__(self, name):
		self._name = name
		# save on normal program termination
		atexit.register(self.save)

	def load(self):
		state = {}
		try:
			with open(self.get_filename(), 'r') as inp:
				state = yaml.safe_load(inp)
		except FileNotFoundError:
			pass
		for a in self.attrs():
			if a in state:
				setattr(self, a, state[a])
		# end for	

	def save(self):
		state = { a: getattr(self, a) for a in self.attrs() }
		with open(self.get_filename(), 'w') as out:
			yaml.dump(state, out)

	def get_filename(self):
		return self._name + '.yml'

	def attrs(self):
		return [a for a in dir(self) if not a.startswith('_') and not callable(getattr(self, a))]
# end class
	

#-------------------------------------------------------------------------------
# functions
#-------------------------------------------------------------------------------
#
def load_file(filename):
	ext = file_ext(filename).lower()
	if ext in ['.yml', '.yaml']:
		with open(filename, 'r') as inp:
			return yaml.safe_load(inp)
	else:
		# assume some text file
		with open(filename, 'r') as inp:
			return inp.read()
	# end if
# end function
	
def save_file(filename, content):
	with open(filename, 'w') as out:
		return out.write(content)

def extract_code_blocks(markdown_text, label):
    pattern = fr"# {label}: (.*?)\n```(.*?)\n(.*?)```"
    matches = re.findall(pattern, markdown_text, re.DOTALL)
    return [(match[0].strip(), match[2].strip()) for match in matches]
# end function

#-------------------------------------------------------------------------------
#
def file_ext(filename):
	return os.path.splitext(filename)[1]
# end function

#-------------------------------------------------------------------------------
#
def from_here(rel_path):
	return os.path.join(os.path.dirname(os.path.realpath(__file__)), rel_path)

#-------------------------------------------------------------------------------
#
def from_home(rel_path):
	return os.path.join(os.path.expanduser("~"), rel_path)

#-------------------------------------------------------------------------------
#
def error(msg):
	error_console.print("\n[bold red]ERROR[/bold red]: %s" % msg)

#-------------------------------------------------------------------------------
#
def warn(msg):
	error_console.print("[bold yellow]WARNING[/bold yellow]: %s" % msg)

#-------------------------------------------------------------------------------
#
def print_markdown(md):
	console.print(Markdown(md))

#-------------------------------------------------------------------------------
# initialization
#-------------------------------------------------------------------------------
#
# load program info
m = metadata("hansli")
prog = ProgInfo(
	name         = m['Name'],
	version      = m['Version'],
	description  = m['Summary'],
	website      = m['Project-URL'].split(' ')[-1],
	bugtracker   = '(unknown)',
)

#-------------------------------------------------------------------------------
# end of file

