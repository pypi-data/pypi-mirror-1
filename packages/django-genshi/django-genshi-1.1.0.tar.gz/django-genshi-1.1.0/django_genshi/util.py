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
		
