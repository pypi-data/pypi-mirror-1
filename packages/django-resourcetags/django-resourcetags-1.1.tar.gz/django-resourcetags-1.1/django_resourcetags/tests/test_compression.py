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
		
