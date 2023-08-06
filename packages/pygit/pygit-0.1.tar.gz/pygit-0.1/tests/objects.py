#!/usr/bin/env python
# -*- coding: utf-8 -*-

import exceptions
import os
import shutil
import tempfile
import unittest

import git
from misc import *

class CommitTests(unittest.TestCase):
    def __init__(self, *args):
        unittest.TestCase.__init__(self, *args)
        self.dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    def setUp(self):
        self.repo = git.Repository(self.dir)
        self.commit = self.repo.heads['refs/heads/master']

    def test_root_tree(self):
        obj = self.commit.tree['tests']['runtests.py']
        self.assertEqual(obj.root, self.commit.tree)

    def test_dirty_blob(self):
        obj = self.commit.tree['tests']['runtests.py']
        obj.contents = 'Foo'
        self.assert_(obj.name is None)
        self.assert_(self.commit.name is None)

    def test_dirty_tree(self):
        tree = self.commit.tree['tests']
        blob = git.Blob(self.repo)
        blob.contents = 'Foo'
        tree['testfile'] = blob

        self.assert_(tree.name is None)
        self.assert_(self.commit.name is None)

    def tearDown(self):
        del self.commit
        del self.repo

class BlobTests(unittest.TestCase):
    def __init__(self, *args):
        unittest.TestCase.__init__(self, *args)
        self.dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    def setUp(self):
        self.repo = git.Repository(self.dir)
        self.commit = self.repo.heads['refs/heads/master']

    def test_content_loaded(self):
        o = self.commit.tree['tests']['runtests.py']
        self.assert_(o.contents.startswith('#!'))

    def tearDown(self):
        del self.commit
        del self.repo

def test_suite():
    suite = unittest.TestSuite()
    suite.addTests(unittest.makeSuite(CommitTests))
    suite.addTests(unittest.makeSuite(BlobTests))
    return suite

