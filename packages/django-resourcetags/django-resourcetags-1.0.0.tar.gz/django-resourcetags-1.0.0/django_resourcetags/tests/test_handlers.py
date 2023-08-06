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
		
