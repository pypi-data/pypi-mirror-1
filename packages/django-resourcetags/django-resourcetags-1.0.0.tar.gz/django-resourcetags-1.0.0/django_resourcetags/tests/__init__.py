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
	
