import unittest
from .. import compression

class CompressionTests (unittest.TestCase):
	def test_compress_javascript (self):
		files = ('application/javascript', ['test1.js', 'test2.js'])
		compressed = compression.compress (*files)
		expected = "<-js->var test1;var test2;<-js->"
		self.assertEqual (compressed, expected)
		
	def test_compress_css (self):
		files = ('text/css', ['test1.css', 'test2.css'])
		compressed = compression.compress (*files)
		expected = "<-css->test1 {}test2 {}<-css->"
		self.assertEqual (compressed, expected)
		
