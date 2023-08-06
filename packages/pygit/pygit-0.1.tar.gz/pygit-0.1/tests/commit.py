import os
import shutil
import tempfile
import unittest

import git

class CommitCreationTests(unittest.TestCase):
    def setUp(self):
        self.repo_dir = tempfile.mkdtemp('.git', self.__class__.__name__)
        self.repo = git.Repository(self.repo_dir, create=True)

    def test_create_commit(self):
        commit = git.Commit(self.repo, refname='refs/heads/master')
        
        blob = git.Blob(self.repo)
        blob.contents = 'Hello'

        tree = git.Tree(self.repo)
        tree['test1'] = blob
        
        commit.tree['tree'] = tree
        commit.commit()

        self.assertEqual(blob.name,        '5ab2f8a4323abafb10abb68657d9d39f1a775057')
        self.assertEqual(tree.name,        'd1328035f0645b43e3aa83d545d4a1bc83593458')
        self.assertEqual(commit.tree.name, '72f9a711fad027d5eda10f31b2f11b754b61a453')

    def test_create_commit_from_parent(self):
        self.test_create_commit()

        blob = git.Blob(self.repo)
        blob.contents = 'World!'

        commit = self.repo.heads['refs/heads/master']
        commitname = commit.name

        tree = commit.tree['tree']
        self.assert_(isinstance(tree, git.Tree))

        commit.tree['test2'] = blob
        self.assert_(commit.name is None)
        commit.commit()

        self.assertEqual(blob.name,        'e5b8f9cece335aca583406109216173174068c73')
        self.assertEqual(tree.name,        'd1328035f0645b43e3aa83d545d4a1bc83593458')
        self.assertEqual(commit.tree.name, 'eab715680ee0fd2f1b0ba82a2f1667769b9401e1')

        self.assertEqual(commit.parents[0].name, commitname)
        self.assertEqual(commit, self.repo.heads['refs/heads/master'])

    def tearDown(self):
        del self.repo
        shutil.rmtree(self.repo_dir)
        pass

def test_suite():
    suite = unittest.TestSuite()
    suite.addTests(unittest.makeSuite(CommitCreationTests))
    return suite
