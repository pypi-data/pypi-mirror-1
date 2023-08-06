import unittest
from action_test_base import *

class TestSeeButton(ActionTestBase):
		
	def get_pattern(self, culture):
		return "test_see_button_%s.acc" % culture
	
	def test_each_language(self):
		self.run_tests()
	
if __name__ == "__main__":
    unittest.main()
