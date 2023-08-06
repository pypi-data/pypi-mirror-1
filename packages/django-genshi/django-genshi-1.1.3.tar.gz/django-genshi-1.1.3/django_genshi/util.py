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

from django.core.exceptions import ImproperlyConfigured
from django.utils import functional

def memoize (cache, num_args):
	def decorator (func):
		return functional.memoize (func, cache, num_args)
	return decorator
	
def load_module_attr (path):
	module, attr = path.rsplit ('.', 1)
	try:
		mod = __import__ (module, {}, {}, [attr])
	except ImportError, error:
		raise ImproperlyConfigured ("Error importing module %r: \"%s\"" % (module, error))
	try:
		return getattr (mod, attr)
	except AttributeError:
		raise ImproperlyConfigured ("Module %r does not define the %r attribute." % (module, attr))
		
