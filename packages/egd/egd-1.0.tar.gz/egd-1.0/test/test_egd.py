#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This module tests egd.py using unittest.

"""

import unittest
import egd

class EgdTest(unittest.TestCase):
    """This class contains test cases for egd.

    """
    def testBlocking(self):
        self.assertEqual(len(egd.get_random_bytes(1)), 1)
        self.assertEqual(len(egd.get_random_bytes(2)), 2)
        self.assertEqual(len(egd.get_random_bytes(32)), 32)
        self.assertEqual(len(egd.get_random_bytes(128)), 128)
        self.assertEqual(len(egd.get_random_bytes(255)), 255)
        self.assertEqual(len(egd.get_random_bytes(256)), 256)
        self.assertEqual(len(egd.get_random_bytes(345)), 345)
    def testRandomness(self):
        self.assertNotEqual(egd.get_random_bytes(20), egd.get_random_bytes(20))

def run_all_tests():
    unittest.main()
    
if __name__ == '__main__':
    run_all_tests()

# end file
