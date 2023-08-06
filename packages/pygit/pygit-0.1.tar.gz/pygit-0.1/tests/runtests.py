#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import unittest

path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, path)

import gitbinary
import repository
import objects
import commit

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(gitbinary.test_suite())
    suite.addTest(repository.test_suite())
    suite.addTest(objects.test_suite())
    suite.addTest(commit.test_suite())
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
