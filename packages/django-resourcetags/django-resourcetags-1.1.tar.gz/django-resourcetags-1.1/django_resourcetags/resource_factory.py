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

import os.path
import mimetypes
from django.conf import settings
from . import compression

__all__ = [
	'ResourceFactory',
	'FilesystemResourceFactory',
	'CompressedResourceFactory',
]

mimetypes.init ()

def get_mimetype (filename):
	mimetype = mimetypes.guess_type (filename)[0]
	if mimetype:
		return mimetype
	return 'application/octet-stream'
	
def get_mtime (path):
	try:
		return os.path.getmtime (path)
	except OSError:
		return 0
		
class FilesystemResource (object):
	def __init__ (self, name, **kwargs):
		super (FilesystemResource, self).__init__ (**kwargs)
		path = os.path.join (settings.MEDIA_ROOT, name)
		mtime = get_mtime (path)
		
		self.name = name
		self.url = '%s%d/%s' % (settings.MEDIA_URL, mtime, name)
		self.mimetype = get_mimetype (name)
		
class CompressedResource (object):
	def __init__ (self, name, **kwargs):
		super (CompressedResource, self).__init__ (**kwargs)
		self.__path = os.path.join (settings.COMPRESSED_MEDIA_ROOT,
		                            'single', name)
		mtime = get_mtime (self.__path)
		
		self.name = name
		self.url = '%s%d/single/%s' % (settings.COMPRESSED_MEDIA_URL,
		                               mtime, name)
		self.mimetype = get_mimetype (name)
		
	def regenerate (self):
		out_path = self.__path
		
		dirname = os.path.dirname (out_path)
		if not os.path.isdir (dirname):
			os.makedirs (dirname)
			
		text = compression.compress (self.mimetype, self.name)
		open (out_path, 'wb').write (text)
		
class CompressedGroupedResource (object):
	def __init__ (self, name, mimetype, names, **kwargs):
		super (CompressedGroupedResource, self).__init__ (**kwargs)
		ext = mimetypes.guess_extension (mimetype)
		self.__path = os.path.join (settings.COMPRESSED_MEDIA_ROOT,
		                            'groups', name + ext)
		mtime = get_mtime (self.__path)
		
		self.name = name
		self.names = tuple (names)
		self.mimetype = mimetype
		root_url = settings.COMPRESSED_MEDIA_URL
		self.url = '%s%d/groups/%s%s' % (root_url, mtime, name, ext)
		
	def regenerate (self):
		out_path = self.__path
		dirname = os.path.dirname (out_path)
		if not os.path.isdir (dirname):
			os.makedirs (dirname)
			
		text = compression.compress (self.mimetype, self.names)
		open (out_path, 'wb').write (text)
		
class ResourceFactory (object):
	def get_resource (self, name):
		raise NotImplementedError
		
	def get_resource_group (self, name):
		raise NotImplementedError
		
class FilesystemResourceFactory (ResourceFactory):
	resource_class = FilesystemResource
	
	def get_resource (self, name):
		return self.resource_class (name)
		
	def get_resource_group (self, name):
		names = settings.RESOURCE_GROUPS[name]
		return map (self.get_resource, names)
		
class CompressedResourceFactory (ResourceFactory):
	def get_resource (self, name):
		if name in settings.COMPRESS_EXTRA:
			return CompressedResource (name)
		return FilesystemResource (name)
		
	def get_resource_group (self, name):
		names = settings.RESOURCE_GROUPS[name]
		grouped = self._group_by_mimetype (names)
		return [CompressedGroupedResource (name, mtype, mtype_names)
		        for mtype, mtype_names in grouped]
		
	def _group_by_mimetype (self, names):
		groups = {}
		for name in names:
			mtype = get_mimetype (name)
			resources = groups.setdefault (mtype, [])
			resources.append (name)
			
		return sorted (groups.items (), key = lambda pair: pair[0])
		
