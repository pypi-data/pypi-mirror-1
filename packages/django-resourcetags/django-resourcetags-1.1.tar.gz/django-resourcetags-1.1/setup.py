from os.path import dirname, join
from setuptools import setup

version = '1.1'

setup (
	name = 'django-resourcetags',
	version = version,
	description = "Django template tags for referencing static files",
	long_description = open (join (dirname (__file__), 'README.txt')).read (),
	author = "John Millikin",
	author_email = "jmillikin@gmail.com",
	license = "GPL",
	url = "https://launchpad.net/django-resourcetags",
	download_url = "http://pypi.python.org/pypi/django-resourcetags/%s" % version,
	platforms = ["Platform Independent"],
	packages = [
		'django_resourcetags',
		'django_resourcetags.compression',
		'django_resourcetags.management',
		'django_resourcetags.management.commands',
		'django_resourcetags.templatetags',
		'django_resourcetags.tests',
	],
	classifiers = [
		"Development Status :: 4 - Beta",
		"Framework :: Django",
		"Intended Audience :: Developers",
		"License :: OSI Approved :: GNU General Public License (GPL)",
		"Operating System :: OS Independent",
		"Programming Language :: Python",
		"Topic :: Internet :: WWW/HTTP :: Dynamic Content",
		"Topic :: Software Development :: Libraries :: Python Modules",
	],
	keywords = ["django"],
	test_suite = 'django_resourcetags.tests.suite',
	install_requires = [
		"Django>=1.0_final",
	],
)
