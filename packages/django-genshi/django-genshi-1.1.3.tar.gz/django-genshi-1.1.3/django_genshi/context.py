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

from itertools import chain
from django.conf import settings
import genshi.template

from django_genshi.util import load_module_attr, memoize

__all__ = ['Context', 'RequestContext']

@memoize ({}, 0)
def get_standard_processors ():
	return map (load_module_attr, settings.TEMPLATE_CONTEXT_PROCESSORS)
	
class Context (genshi.template.Context):
	"""Wrapper class so instances of ``genshi.template.Context``
	can be constructed using the same style as
	``django.template.Context``.
	
	"""
	def __init__ (self, dict_ = None):
		if dict_ is None:
			dict_ = {}
			
		super (Context, self).__init__ (**dict_)
		
class RequestContext (Context):
	def __init__(self, request, dict_ = None, processors = ()):
		super (RequestContext, self).__init__ (dict_)
		for processor in chain (get_standard_processors (), processors):
			self.update (processor (request))
			
