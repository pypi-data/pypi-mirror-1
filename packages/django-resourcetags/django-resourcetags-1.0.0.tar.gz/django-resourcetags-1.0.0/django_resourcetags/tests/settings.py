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
