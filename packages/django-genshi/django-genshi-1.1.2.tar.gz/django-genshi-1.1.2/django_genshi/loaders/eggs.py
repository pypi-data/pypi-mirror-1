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
