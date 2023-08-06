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

from genshi.builder import tag
from django.conf import settings
from . import handlers, resource_factory

__all__ = ['template_context']

def js_handler (url):
	return tag.script (type = 'text/javascript', src = url)
	
def css_handler (url):
	return tag.link (type = 'text/css', rel = 'stylesheet', href = url)
	
def img_handler (url):
	return tag.img (src = url, alt = "")
	
DEFAULT_HANDLERS = {
	'application/javascript': js_handler,
	'text/css': css_handler,
	'image/png': img_handler,
	'image/jpeg': img_handler,
	'image/gif': img_handler,
}

class TagBuilder (object):
	def __init__ (self, factory):
		self._factory = factory
		
	def resource_tag (self, resource_name):
		resource = self._factory.get_resource (resource_name)
		handler = self.get_handler (resource.mimetype)
		return handler (resource.url)
		
	def resource_url (self, resource_name):
		resource = self._factory.get_resource (resource_name)
		return resource.url
		
	def resource_group_tag (self, group_name):
		group = self._factory.get_resource_group (group_name)
		def _get_tags ():
			for resource in group:
				handler = self.get_handler (resource.mimetype)
				yield handler (resource.url)
		return tag (*_get_tags ())
		
	def get_handler (self, mimetype):
		return handlers.get_handler (mimetype, DEFAULT_HANDLERS)
		
def template_context (request):
	if getattr (settings, 'COMPRESS_MEDIA', False):
		factory = resource_factory.CompressedResourceFactory ()
	else:
		factory = resource_factory.FilesystemResourceFactory ()
	builder = TagBuilder (factory)
	return dict (
		resource = builder.resource_tag,
		resource_url = builder.resource_url,
		resource_group = builder.resource_group_tag,
	)
	
