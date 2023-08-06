import logging
from django.conf import settings
from genshi.template.loader import TemplateLoader, TemplateNotFound

from django_genshi.util import memoize, load_module_attr

__all__ = ['get_template', 'select_template', 'TemplateNotFound']

log = logging.getLogger (__name__)

def _genshi_template_loadfunc (template_name, load_funcs):
	for loader_name, loader in load_funcs:
		try:
			info = loader (template_name)
		except StandardError:
			log.error ("Error calling template loader %r", loader_name,
			           exc_info = 1)
			continue
		if info is not None:
			return info
			
	raise TemplateNotFound (template_name, [])
	
def _get_load_func (path):
	func = load_module_attr (path)
	if func.is_usable:
		return func
		
	log.warning ("Your GENSHI_TEMPLATE_LOADERS setting includes %r,"
	             " but your Python installation doesn't support"
	             " that type of template loading. Consider"
	             " removing that line from"
	             " GENSHI_TEMPLATE_LOADERS.", path)
	
@memoize ({}, 0)
def _get_loader ():
	loader_paths = getattr (settings, 'GENSHI_TEMPLATE_LOADERS', ())
	loaders = ((path, _get_load_func (path)) for path in loader_paths)
	load_funcs = tuple ((p, l) for p, l in loaders if l)
	
	def genshi_loader_wrapper (name):
		return _genshi_template_loadfunc (name, load_funcs)
		
	return TemplateLoader (
		[genshi_loader_wrapper],
		variable_lookup = 'strict',
		auto_reload = True,
	)
	
def get_template (template_name):
	loader = _get_loader ()
	return loader.load (template_name, relative_to = '/')
	
def select_template (template_name_list):
	loader = _get_loader ()
	for name in template_name_list:
		try:
			return loader.load (name, relative_to = '/')
		except TemplateNotFound:
			pass
	raise TemplateNotFound (', '.join (template_name_list), [])
	
