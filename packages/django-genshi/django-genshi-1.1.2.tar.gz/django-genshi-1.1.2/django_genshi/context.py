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
			
