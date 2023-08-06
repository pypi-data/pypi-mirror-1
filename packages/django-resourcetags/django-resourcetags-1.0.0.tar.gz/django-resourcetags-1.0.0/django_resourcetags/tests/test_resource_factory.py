import unittest
import os.path
from os.path import getmtime, join, isdir
from django.conf import settings
from .. import resource_factory

def ensure_exists (path):
	dirname = os.path.dirname (path)
	
	# Ensure the file exists
	if not isdir (dirname):
		os.makedirs (dirname)
	open (path, 'ab').write ('')
	
class TestFilesystemResourceFactory (unittest.TestCase):
	def test_get_resource_params (self):
		factory = resource_factory.FilesystemResourceFactory ()
		resource = factory.get_resource ('resource.txt')
		self.assertEqual (resource.name, 'resource.txt')
		
	def test_get_resource_group (self):
		factory = resource_factory.FilesystemResourceFactory ()
		group = factory.get_resource_group ('css-group')
		self.assertEqual (len (group), 2)
		self.assertEqual (group[0].name, 'test1.css')
		self.assertEqual (group[1].name, 'test2.css')
		
class TestCompressedResourceFactory (unittest.TestCase):
	def test_get_resource (self):
		factory = resource_factory.CompressedResourceFactory ()
		resource = factory.get_resource ('test.txt')
		self.assertEqual (resource.name, 'test.txt')
		self.assert_ (resource.url.startswith (settings.COMPRESSED_MEDIA_URL))
		
	def test_get_resource_not_compressed (self):
		factory = resource_factory.CompressedResourceFactory ()
		resource = factory.get_resource ('test2.txt')
		self.assertEqual (resource.name, 'test2.txt')
		self.assert_ (resource.url.startswith (settings.MEDIA_URL))
		
	def test_get_resource_group (self):
		factory = resource_factory.CompressedResourceFactory ()
		group = factory.get_resource_group ('css-group')
		self.assertEqual (len (group), 1)
		self.assertEqual (group[0].name, 'css-group')
		self.assertEqual (group[0].names, ('test1.css', 'test2.css'))
		self.assertEqual (group[0].mimetype, 'text/css')
		
	def test_get_resource_group_mixed (self):
		factory = resource_factory.CompressedResourceFactory ()
		group = factory.get_resource_group ('mixed-group')
		self.assertEqual (len (group), 2)
		self.assertEqual (group[0].name, 'mixed-group')
		self.assertEqual (group[0].names, ('test1.css', 'test2.css'))
		self.assertEqual (group[0].mimetype, 'text/css')
		self.assertEqual (group[1].name, 'mixed-group')
		self.assertEqual (group[1].names, ('test1.txt', 'test2.txt'))
		self.assertEqual (group[1].mimetype, 'text/plain')
		
class TestFilesystemResource (unittest.TestCase):
	def test_url (self):
		resource = resource_factory.FilesystemResource ('test.txt')
		mtime = getmtime (join (settings.MEDIA_ROOT, 'test.txt'))
		self.assertEqual (resource.url, '/media/root/%d/test.txt' % mtime)
		
	def test_url_noexist (self):
		resource = resource_factory.FilesystemResource ('test-noexist.txt')
		self.assertEqual (resource.url, '/media/root/0/test-noexist.txt')
		
	def test_mimetype (self):
		resource = resource_factory.FilesystemResource ('test.txt')
		self.assertEqual (resource.mimetype, 'text/plain')
		
	def test_mimetype_unknown (self):
		resource = resource_factory.FilesystemResource ('test')
		self.assertEqual (resource.mimetype, 'application/octet-stream')
		
class TestCompressedResource (unittest.TestCase):
	def test_url (self):
		file_path = join (settings.COMPRESSED_MEDIA_ROOT, 'single', 'test.txt')
		ensure_exists (file_path)
		mtime = getmtime (file_path)
		
		resource = resource_factory.CompressedResource ('test.txt')
		self.assertEqual (resource.url, '/media/compressed/%d/single/test.txt' % mtime)
		
	def test_url_noexist (self):
		resource = resource_factory.CompressedResource ('test-noexist.txt')
		self.assertEqual (resource.url, '/media/compressed/0/single/test-noexist.txt')
		
	def test_mimetype (self):
		resource = resource_factory.CompressedResource ('test.txt')
		self.assertEqual (resource.mimetype, 'text/plain')
		
	def test_mimetype_unknown (self):
		resource = resource_factory.CompressedResource ('test')
		self.assertEqual (resource.mimetype, 'application/octet-stream')
		
class TestCompressedResourceGroup (unittest.TestCase):
	def test_url (self):
		file_path = join (settings.COMPRESSED_MEDIA_ROOT, 'groups', 'css-group.css')
		ensure_exists (file_path)
		mtime = getmtime (file_path)
		
		group = resource_factory.CompressedGroupedResource ('css-group', 'text/css', ())
		self.assertEqual (group.url, '/media/compressed/%d/groups/css-group.css' % mtime)
		
	def test_url_noexist (self):
		group = resource_factory.CompressedGroupedResource ('noexist', 'text/css', ())
		self.assertEqual (group.url, '/media/compressed/0/groups/noexist.css')
		
