# -*- coding: utf-8 -*-
""" base.py low-level tests
"""
import unittest
import os

from collective.releaser.base import safe_input

class BaseTest(unittest.TestCase):

    def test_safe_input(self):
        def my_input(msg):
            return ''
        safe_input.func_globals['raw_input'] = my_input
        self.assertEquals(safe_input('value'), None)
        self.assertEquals(safe_input('value', 10), 10)
        

def test_suite():
    """returns the test suite"""
    return unittest.makeSuite(BaseTest)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')


