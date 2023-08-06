# Copyright (C) 2008-2009 John Millikin <jmillikin@gmail.com>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

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
			
