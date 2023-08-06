import unittest
from os.path import join, getmtime

from django.conf import settings
from django.template import Template

class TemplateTagTests (unittest.TestCase):
	def test_resource_url (self):
		tmpl_string = "{% load resources %}{% resource_url '&test.txt' %}"
		tmpl = Template (tmpl_string)
		self.assertEqual (tmpl.render ({}), "/media/root/0/%26test.txt")
		
	def test_resource (self):
		mtime = getmtime (join (settings.MEDIA_ROOT, 'test1.css'))
		
		tmpl_string = "{% load resources %}{% resource '&test1.css' %}"
		tmpl = Template (tmpl_string)
		self.assertEqual (tmpl.render ({}),
			'<link type="text/css" rel="stylesheet" href="/media/root/0/%26test1.css" />')
		
	def test_resource_group (self):
		tmpl_string = "{% load resources %}{% resource_group 'escaped group' %}"
		tmpl = Template (tmpl_string)
		self.assertEqual (tmpl.render ({}),
			('<link type="text/css" rel="stylesheet" href="/media/root/0/%26test1.css" />\n'
			 '<link type="text/css" rel="stylesheet" href="/media/root/0/%26test2.css" />'
			))
		
