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

from __future__ import with_statement
import unittest
from .. import handlers
from ..genshi_integration import TagBuilder
from . import mocking

def MockResource (mimetype, url):
	controller = mocking.MockController ()
	controller.attrs (mimetype = mimetype, url = url)
	return controller
	
def MockResourceGroup (*resources):
	controller = mocking.MockController ()
	mocked_resources = [MockResource (*r).recorder for r in resources]
	controller.methods (__iter__ = iter (mocked_resources))
	return controller
	
def MockResourceFactory (mimetype, url):
	resource = MockResource (mimetype, url)
	factory = mocking.MockController ()
	factory.methods (get_resource = resource.recorder)
	return factory
	
class TestTagBuilder (unittest.TestCase):
	def test_resource_tag (self):
		factory = MockResourceFactory ('mimetype', 'url')
		builder = TagBuilder (factory.recorder)
		
		handler = mocking.StubbedMethod ("handler output")
		builder.get_handler = mocking.StubbedMethod (handler)
		
		tag = builder.resource_tag ('app/index.css')
		self.assertEqual (tag, "handler output")
		self.assertEqual (builder.get_handler.calls, [
			(('mimetype',), {}),
		])
		self.assertEqual (handler.calls, [
			(('url',), {}),
		])
		with factory.playback () as p:
			p.get_resource ('app/index.css')
			
	def test_resource_url (self):
		factory = MockResourceFactory ('mimetype', 'url')
		builder = TagBuilder (factory.recorder)
		
		url = builder.resource_url ('app/index.css')
		self.assertEqual (url, "url")
		with factory.playback () as p:
			p.get_resource ('app/index.css')
			
	def test_resource_group_tag (self):
		group = MockResourceGroup (('mimetype1', 'url1'),
		                           ('mimetype2', 'url2'),
		                           ('mimetype3', 'url3'))
		factory = mocking.MockController ()
		factory.methods (get_resource_group = group.recorder)
		builder = TagBuilder (factory.recorder)
		
		handler = mocking.StubbedMethod ("handler ")
		builder.get_handler = mocking.StubbedMethod (handler)
		
		tags = builder.resource_group_tag ('group1')
		self.assertEqual (unicode (tags), 'handler handler handler ')
		self.assertEqual (builder.get_handler.calls, [
			(('mimetype1',), {}),
			(('mimetype2',), {}),
			(('mimetype3',), {}),
		])
		with factory.playback () as p:
			p.get_resource_group ('group1')
			
	def test_has_default_handlers (self):
		builder = TagBuilder (None)
		for mimetype in ('text/css', 'application/javascript', 'image/png'):
			builder.get_handler (mimetype)
			
	def test_get_handler_invalid (self):
		builder = TagBuilder (None)
		try:
			builder.get_handler ('invalid')
			self.fail ("No exception raised")
		except handlers.NoHandlerFound, exc:
			self.assertEqual (exc.mimetype, 'invalid')
			
