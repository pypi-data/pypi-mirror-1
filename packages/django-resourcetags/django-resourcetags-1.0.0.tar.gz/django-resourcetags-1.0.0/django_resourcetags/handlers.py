from django.conf import settings
from .util import load_module_attr, memoize

__all__ = ['get_handler']

MIMETYPE_OVERRIDES = {
	'application/x-javascript': 'application/javascript',
	'text/javascript': 'application/javascript',
}

class NoHandlerFound (Exception):
	def __init__ (self, mimetype):
		super (NoHandlerFound, self).__init__ (mimetype)
		self.mimetype = mimetype
		
	def __str__ (self):
		msg = "No handler found for mimetype %r"
		return msg % (self.mimetype,)
		
@memoize ({}, 0)
def get_handlers ():
	handlers = {}
	handler_names = getattr (settings, 'RESOURCE_HANDLERS', {})
	for mimetype, name in handler_names.items ():
		handlers[mimetype] = load_module_attr (name)
	return handlers
	
def get_handler (mimetype, default_handlers):
	handlers = get_handlers ()
	mimetype = MIMETYPE_OVERRIDES.get (mimetype, mimetype)
	try:
		return handlers[mimetype]
	except KeyError:
		try:
			return default_handlers[mimetype]
		except KeyError:
			raise NoHandlerFound (mimetype)
			
