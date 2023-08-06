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
from django.http import HttpResponse

from django_genshi.context import Context
from django_genshi.loader import get_template, select_template
from django_genshi.util import memoize, load_module_attr

__all__ = ['render_to_stream', 'render_to_response',
           'render_to_response_autodetect']

XHTML_CONTENT_TYPE = 'application/xhtml+xml'

def _stream_to_response (stream, charset, output_type, content_type):
	filtered = stream.filter (*_get_filters ())
	
	text = filtered.render (output_type, encoding = charset,
	                        strip_whitespace = False)
	full_content_type = '%s; charset=%s' % (content_type, charset)
	return HttpResponse (text, content_type = full_content_type)
	
@memoize ({}, 0)
def _get_filters ():
	names = getattr (settings, 'GENSHI_TEMPLATE_FILTERS', ())
	return tuple (map (load_module_attr, names))
	
def render_to_stream (template_name, dictionary = None,
                      context_instance = None):
	"""Render a template and data into a Genshi markup stream."""
	if dictionary is None:
		dictionary = {}
	if isinstance (template_name, (list, tuple)):
		template = select_template (template_name)
	else:
		template = get_template (template_name)
		
	if context_instance:
		context_instance.update (dictionary)
	else:
		context_instance = Context (dictionary)
		
	return template.generate (context_instance)
	
def render_to_response (*args, **kwargs):
	"""Render a template and data into an ``HttpResponse``."""
	charset = settings.DEFAULT_CHARSET
	content_type = settings.DEFAULT_CONTENT_TYPE
	
	stream = render_to_stream (*args, **kwargs)
	return _stream_to_response (stream, charset, 'html', content_type)
	
def render_to_response_autodetect (request, template_name,
                                   dictionary = None,
                                   context_instance = None):
	"""Render a template and context into an ``HttpResponse``, with
	output autodetection.
	
	The main purpose of this function is to let templates that a valid
	both as HTML and XHTML be rendered in the correct format, based on
	the HTTP ``Accept`` header.
	
	"""
	from genshi.core import DOCTYPE
	from genshi.output import DocType
	
	def _get_content_type ():
		if request is not None:
			if XHTML_CONTENT_TYPE in request.META.get ('HTTP_ACCEPT', ''):
				return 'xml', 'xhtml11', XHTML_CONTENT_TYPE
		return 'html', 'html', 'text/html'
		
	def replace_doctype (stream):
		for kind, data, pos in stream:
			if kind == DOCTYPE:
				yield kind, DocType.get (doctype), pos
			else:
				yield kind, data, pos
				
	charset = settings.DEFAULT_CHARSET
	output_type, doctype, content_type = _get_content_type ()
	
	stream = render_to_stream (template_name, dictionary, context_instance)
	stream = stream.filter (replace_doctype)
	return _stream_to_response (stream, charset, output_type, content_type)
	
