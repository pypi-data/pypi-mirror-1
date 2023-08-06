#!/usr/bin/env python
# -*- coding: utf-8 -*-

#__all__ = ['RepositoryTestSuite']

import os
import unittest

from git.gitbinary import GitBinary
from misc import *

class GitBinaryTests(unittest.TestCase):
    def __init__(self, *args):
        unittest.TestCase.__init__(self, *args)
        self.work_tree = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        self.git_dir = os.path.join(self.work_tree, '.git')

    def setUp(self):
        self.bin = GitBinary(self.work_tree)

    def test_git_dir_is_okay(self):
        git_dir = self.bin('rev-parse', '--git-dir', wait=1).strip()
        self.assertEqual(git_dir, self.git_dir)
       
    def test_with_generator(self):
        for i in self.bin('rev-list', 'HEAD', '^HEAD~5'):
            pass


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests(unittest.makeSuite(GitBinaryTests))
    return suite

