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
		
