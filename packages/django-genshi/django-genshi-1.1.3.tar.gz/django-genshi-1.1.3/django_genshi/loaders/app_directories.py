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

from os.path import dirname, join
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django_genshi.loaders.filesystem import load_template as filesystem_loader
from django_genshi.util import memoize

__all__ = ['load_template']

@memoize ({}, 0)
def get_template_dirs ():
	template_dirs = []
	for app in settings.INSTALLED_APPS:
		i = app.rfind ('.')
		if i == -1:
			m, a = app, None
		else:
			m, a = app[:i], app[i+1:]
		try:
			if a is None:
				mod = __import__ (m, {}, {}, [])
			else:
				mod = getattr (__import__ (m, {}, {}, [a]), a)
		except ImportError, e:
			raise ImproperlyConfigured ("ImportError %s: %s" % (app, e.args[0]))
			
		template_dirs.append (join (dirname (mod.__file__), 'templates'))
	return template_dirs
	
def load_template (template_name):
	return filesystem_loader (template_name, get_template_dirs ())
	
load_template.is_usable = True
