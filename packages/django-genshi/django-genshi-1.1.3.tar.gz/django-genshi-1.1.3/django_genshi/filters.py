# Copyright (C) 2008-2009 John Millikin

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Useful template stream processing filters."""

import re
from genshi.core import START, START_NS, TEXT, END, END_NS

IGNORED_ELEMENTS = ('pre', 'textarea')
COLLAPSE_REGEX = re.compile (r'[ \t\n\r\f\v]+')
def collapse (text):
	"""Collapse long runs of whitespace to a single space. If
	the whitespace contains a newline, it is collapsed to a
	single newline.
	
	>>> collapse ('   ')
	' '
	>>> collapse (' \\n\\n ')
	'\\n'
	>>> collapse ('test  test')
	'test test'
	>>> collapse ('test \\n test')
	'test test'
	
	"""
	if text.isspace ():
		if "\n" in text:
			return "\n"
		return " "
	ret_type = type (text)
	return ret_type (COLLAPSE_REGEX.sub (" ", text))
	
def strip_whitespace (stream):
	"""Strip all unneeded whitespace from the stream."""
	state_stack = []
	for kind, data, pos in stream:
		if kind == START:
			element, _ = data
			if element.localname in IGNORED_ELEMENTS:
				state_stack.append (False)
			else:
				state_stack.append (True)
			yield kind, data, pos
		elif kind == START_NS:
			state_stack.append (True)
			yield kind, data, pos
		elif kind in (END, END_NS):
			state_stack.pop ()
			yield kind, data, pos
		elif kind == TEXT:
			if state_stack[-1]:
				yield kind, collapse (data), pos
			else:
				yield kind, data, pos
		else:
			yield kind, data, pos
			
if __name__ == '__main__':
	import doctest
	doctest.testmod ()
