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

from django.conf import settings
try:
	from pkg_resources import resource_stream
except ImportError:
	resource_stream = None
	
__all__ = ['load_template']

def load_template (template_name):
	assert resource_stream
	tmpl_path = 'templates/' + template_name
	for app in settings.INSTALLED_APPS:
		try:
			fileobj = resource_stream (app, tmpl_path)
		except IOError:
			continue
		return tmpl_path, template_name, fileobj, None
		
load_template.is_usable = (resource_stream is not None)
