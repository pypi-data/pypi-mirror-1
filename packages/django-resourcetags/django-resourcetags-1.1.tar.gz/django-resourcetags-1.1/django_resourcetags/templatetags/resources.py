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

import logging
import urllib
from django import template
from django.conf import settings
register = template.Library()

from django_resourcetags import resource_factory, handlers

log = logging.getLogger (__name__)

def js_handler (url):
	url = urllib.quote (url)
	return '<script type="text/javascript" src="%s"></script>' % url
	
def css_handler (url):
	url = urllib.quote (url)
	return '<link type="text/css" rel="stylesheet" href="%s" />' % url
	
def img_handler (url):
	url = urllib.quote (url)
	return '<img src="%s" alt=""/>' % url
	
DEFAULT_HANDLERS = {
	'application/javascript': js_handler,
	'text/css': css_handler,
	'image/png': img_handler,
	'image/jpeg': img_handler,
	'image/gif': img_handler,
}

_FACTORY = None
def _get_factory ():
	global _FACTORY
	if _FACTORY is not None:
		return _FACTORY
	if getattr (settings, 'COMPRESS_MEDIA', False):
		factory = resource_factory.CompressedResourceFactory ()
	else:
		factory = resource_factory.FilesystemResourceFactory ()
		
	_FACTORY = factory
	return _FACTORY
	
def _get_name (token):
	error = template.TemplateSyntaxError
	try:
		tag_name, resource_name = token.split_contents ()
	except ValueError:
		raise error ("%r tag requires exactly one argument" % token.contents.split ()[0])
		
	if not (resource_name[0] == resource_name[-1] and
	        resource_name[0] in ('"', "'")):
		raise error ("%r tag's argument should be in quotes" % tag_name)
		
	return resource_name[1:-1]
	
def _get_handler (mimetype):
	return handlers.get_handler (mimetype, DEFAULT_HANDLERS)
	
class ResourceNode (template.Node):
	def __init__ (self, resource):
		self.resource = resource
		
	def render (self, context):
		try:
			handler = _get_handler (self.resource.mimetype)
			return handler (self.resource.url)
		except StandardError, exc:
			log.error ("Error rendering ResourceNode: %s", exc, exc_info = True)
			return ""
			
class ResourceGroupNode (template.Node):
	def __init__ (self, group):
		self.group = group
		
	def render (self, context):
		def _get_tags ():
			for resource in self.group:
				try:
					handler = _get_handler (resource.mimetype)
					text = handler (resource.url)
				except StandardError, exc:
					log.error ("Error rendering ResourceGroupNode: %s", exc, exc_info = True)
					text = ""
				yield text
		return "\n".join (_get_tags ())
		
class ResourceURLNode (template.Node):
	def __init__ (self, resource_url):
		self.resource_url = resource_url
		
	def render (self, context):
		return urllib.quote (self.resource_url)
		
@register.tag (name = "resource")
def compile_resource (parser, token):
	resource_name = _get_name (token)
	factory = _get_factory ()
	resource = factory.get_resource (resource_name)
	return ResourceNode (resource)
	
@register.tag (name = "resource_group")
def compile_resource_group (parser, token):
	group_name = _get_name (token)
	factory = _get_factory ()
	group = factory.get_resource_group (group_name)
	return ResourceGroupNode (group)
	
@register.tag (name = "resource_url")
def compile_resource_url (parser, token):
	resource_name = _get_name (token)
	factory = _get_factory ()
	resource = factory.get_resource (resource_name)
	return ResourceURLNode (resource.url)
	
