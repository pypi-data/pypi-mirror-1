#!/usr/bin/env python
# -*- coding: utf-8 -*-

import exceptions
import os
import shutil
import tempfile
import unittest

import git
from misc import *

class BareRepositoryCreationTests(unittest.TestCase):
    def __init__(self, *args):
        unittest.TestCase.__init__(self, *args)
        self.repo_suffix = '.git'

    def setUp(self):
        self.repo_dir = tempfile.mkdtemp(self.repo_suffix, self.__class__.__name__)

    @expect_exception(exceptions.IOError)
    def test_non_existing_dir_raises_exception(self):
        repo = git.Repository('/tmp/this-directory-cannot-exist', create=True)

    @expect_exception(git.InvalidRepositoryError)
    def test_empty_dir_raises_exception(self):
        repo = git.Repository(self.repo_dir)

    def test_create_repository(self):
        repo = git.Repository(self.repo_dir, create=True)

    def tearDown(self):
        if os.path.exists(self.repo_dir):
            shutil.rmtree(self.repo_dir)

class RepositoryCreationTests(BareRepositoryCreationTests):
    def __init__(self, *args):
        BareRepositoryCreationTests.__init__(self, *args)
        self.repo_suffix = ''

class RepositoryTests(unittest.TestCase):
    def __init__(self, *args):
        unittest.TestCase.__init__(self, *args)
        self.dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    def setUp(self):
        self.repo = git.Repository(self.dir)

    def test_description_property(self):
        descr = self.repo.description
        self.assert_(isinstance(descr, str))
        self.repo.description = descr

    def test_daemon_export_property(self):
        de = self.repo.daemon_export
        self.repo.daemon_export = not de
        self.repo.daemon_export = de

    def test_config_property(self):
        repoversion = self.repo.config['core.repositoryformatversion']
        self.assertEqual(repoversion, '0')

    def test_head_property(self):
        self.assert_(isinstance(self.repo.head, git.Commit))

    def test_heads_property(self):
        for name, head in self.repo.heads.iteritems():
            self.assert_(isinstance(name, str))
            self.assert_(isinstance(head, git.Commit))

    def test_rev_list(self):
        n_commits = 0
        for commit in self.repo.rev_list(to='HEAD^^'):
            n_commits += 1
            self.assert_(isinstance(commit, git.Commit))
        self.assert_(n_commits >= 2)

    def test_clone(self, bare=False):
        suffix = bare and '-clone.git' or '-clone'
        # I know this is deprecated and unsafe, but the dir should not exist
        # before git-clone creates it.
        repo_dir = tempfile.mktemp(suffix, self.__class__.__name__)
        try:
            clone = self.repo.clone(repo_dir)
            self.assert_(isinstance(clone, git.Repository))
        finally:
            if os.path.exists(repo_dir):
                shutil.rmtree(repo_dir)

    def test_clone_bare(self):
        self.test_clone(True)

    def tearDown(self):
        del self.repo

def test_suite():
    suite = unittest.TestSuite()
    suite.addTests(unittest.makeSuite(BareRepositoryCreationTests))
    suite.addTests(unittest.makeSuite(RepositoryCreationTests))
    suite.addTests(unittest.makeSuite(RepositoryTests))
    return suite

