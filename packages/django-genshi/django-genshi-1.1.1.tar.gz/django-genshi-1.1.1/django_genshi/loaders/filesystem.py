from os.path import getmtime
from django.conf import settings
from django.utils._os import safe_join

__all__ = ['load_template']

def get_template_sources (template_name, template_dirs):
	for template_dir in template_dirs:
		try:
			yield safe_join (template_dir, template_name)
		except ValueError:
			# The joined path was located outside of template_dir.
			pass
			
def load_template (template_name, template_dirs = None):
	if template_dirs is None:
		template_dirs = settings.TEMPLATE_DIRS
	for filepath in get_template_sources (template_name, template_dirs):
		try:
			fileobj = open (filepath, 'rb')
			mtime = getmtime (filepath)
		except IOError:
			continue
			
		def _uptodate ():
			return mtime == getmtime (filepath)
		return filepath, template_name, fileobj, _uptodate
		
load_template.is_usable = True
