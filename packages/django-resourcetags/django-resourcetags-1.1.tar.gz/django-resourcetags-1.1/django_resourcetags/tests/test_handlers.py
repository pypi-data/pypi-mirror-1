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
from .. import handlers

class HandlerTests (unittest.TestCase):
	def test_no_handler (self):
		try:
			handlers.get_handler ('text/plain', {})
			self.fail ("No exception raised.")
		except handlers.NoHandlerFound, exc:
			self.assertEqual (exc.mimetype, 'text/plain')
			
	def test_default_handlers (self):
		my_handler = object ()
		handler = handlers.get_handler ('text/plain', {'text/plain': my_handler})
		self.assert_ (handler is my_handler)
		
