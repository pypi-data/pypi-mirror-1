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

from django.conf.global_settings import *
from os import path
relative = lambda *paths: path.abspath (path.join (path.dirname (__file__), *paths))

MEDIA_ROOT = relative ('data')
MEDIA_URL = '/media/root/'

COMPRESSED_MEDIA_URL = '/media/compressed/'
COMPRESSED_MEDIA_ROOT = relative ('compressed-media-cache')

RESOURCE_COMPRESSION_FILTERS = {
	'text/css': ('django_resourcetags.tests.css_filter',),
	'application/javascript': ('django_resourcetags.tests.js_filter',),
}

RESOURCE_GROUPS = {
	'css-group': (
		'test1.css',
		'test2.css',
	),
	'mixed-group': (
		'test1.css',
		'test2.css',
		'test1.txt',
		'test2.txt',
	),
	'escaped group': (
		'&test1.css',
		'&test2.css',
	),
}
COMPRESS_EXTRA = ['test.txt']

INSTALLED_APPS = ('django_resourcetags',)
