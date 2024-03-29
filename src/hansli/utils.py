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
import collections
import glob
import os
import re
import signal
import sys

from time import perf_counter as timer
from importlib.metadata import metadata

import yaml

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
class Colors:
    # standard
    RED          = '\x1b[1;31m'
    GREEN        = '\x1b[1;32m'
    YELLOW       = "\x1b[1;33m"
    BLUE         = "\x1b[1;34m"
    PURPLE       = "\x1b[1;35m"
    CYAN         = "\x1b[1;36m"
    WHITE        = "\x1b[1;37m"
    # modifiers
    BOLD         = "\x1b[1m"
    FAINT        = "\x1b[2m"
    ITALIC       = "\x1b[3m"
    UNDERLINE    = "\x1b[4m"
    BLINK        = "\x1b[5m"
    NEGATIVE     = "\x1b[7m"
    CROSSED      = "\x1b[9m"
    # combinations
    LINK         = BLUE + UNDERLINE
    # misc
    RESET        = '\x1b[0m'
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
		self.name = name
	def __del__(self):
		self.save()

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
		return self.name + '.yml'

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

def extract_code_block(markdown_text, language=None):
	start_tag = "```" + language + "\n" if language else "```"
	end_tag = "```"

	start_index = markdown_text.find(start_tag)
	if start_index == -1:
		return ""  # Code block start tag not found

	end_index = markdown_text.find(end_tag, start_index + len(start_tag))
	if end_index == -1:
		return ""  # Code block end tag not found

	return markdown_text[start_index + len(start_tag):end_index]
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

