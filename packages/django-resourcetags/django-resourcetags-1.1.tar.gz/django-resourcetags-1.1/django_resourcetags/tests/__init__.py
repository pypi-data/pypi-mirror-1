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
import logging

logging.basicConfig ()

def css_filter (text):
	return '<-css->%s<-css->' % text
	
def js_filter (text):
	return '<-js->%s<-js->' % text
	
def suite ():
	from django.conf import settings
	from . import settings as test_settings
	if not settings.configured:
		settings.configure (test_settings)
		
	from . import (
		test_compression,
		test_genshi_integration,
		test_handlers,
		test_resource_factory,
		test_templatetags,
	)
	
	UNITTEST_MODULES = [
		test_compression,
		test_genshi_integration,
		test_handlers,
		test_resource_factory,
		test_templatetags,
	]
	
	loader = unittest.TestLoader ()
	tests = unittest.TestSuite ()
	tests.addTests (map (loader.loadTestsFromModule, UNITTEST_MODULES))
	return tests
	
