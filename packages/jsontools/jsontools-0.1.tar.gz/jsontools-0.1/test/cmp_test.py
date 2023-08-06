import unittest

import jsontools

class CmpTest(unittest.TestCase):
    def test_random(self):
        num_tests = 1000
        fj = jsontools.FuzzyJson()
        for obj in fj.generate(num_tests):
            self.assertEqual(jsontools.jsoncmp(obj, obj), True)
