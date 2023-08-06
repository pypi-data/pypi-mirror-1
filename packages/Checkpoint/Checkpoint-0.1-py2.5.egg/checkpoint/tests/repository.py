"""Unit-test the Checkpoint Repository"""

from __future__ import with_statement

import os
import shutil
import tempfile
import unittest

from checkpoint.filestore import FILE
from checkpoint.repository import Repository, Mirror, ADDED, DELETED, MODIFIED
from checkpoint.error import CheckpointError
from checkpoint.util import filter_all_patterns, matches_any_pattern
from checkpoint.tests.filestore import TempFileTestCase


__all__ = ['RepositoryTest', 'MirrorTest']

class RepositoryTest(TempFileTestCase):
    def setUp(self):
        TempFileTestCase.setUp(self)
        
        # Create some files to test with
        self.create_temp_files(self.test_files)
    
    def testInitializeRepository(self):
        """initialize should work"""
        # Initialize a Repository with the test files
        self.repository = Repository(self.temp_dir)
        self.repository.initialize()
        
        # Ensure repository directory was created
        self.assertTrue(os.path.isdir(self.repository.repository_path))
        
        # Ensure filestore and db were initialized
        self.assertTrue(Repository.contains_repository(self.temp_dir))
        self.assertTrue(self.repository.filestore.is_initialized())
        self.assertTrue(self.repository.db.is_initialized())
        
        # Ensure format file was created
        repository_format_file = os.path.join(
            self.repository.repository_path,
            'repository_format'
        )
        self.assertTrue(os.path.exists(repository_format_file))
        
        # Initializing a repository a second time should raise an error.
        self.assertRaises(CheckpointError, self.repository.initialize)
    
    def testDeleteRepository(self):
        """delete should work"""
        # Initialize a Repository to work with
        self.testInitializeRepository()

        # Repository directory should not exist after `delete` is called.
        self.repository.delete_repository()
        self.assertFalse(os.path.isdir(self.repository.repository_path))
        
        # Re-deleting a repository should raise an error
        self.assertRaises(CheckpointError, self.repository.delete_repository)

    def testCommit(self):
        """iter_changes should detect no new changes after commit"""
        self.testInitializeRepository()
        self.repository.commit()
        self.assertTrue(list(self.repository.iter_changes()) == [])

    def testAddFiles(self):
        """iter_changes should detect new files"""
        # Initialize a Repository and commit the files
        self.testCommit()
        
        # Create a new file
        self.new_file = "some-new-file.txt"
        with open(self.format_path(self.new_file), 'w') as f: 
            f.write("hi there")
        
        # Only one change was made, so only one change should be detected.
        changes = list(self.repository.iter_changes())
        self.assertTrue(len(changes) == 1)
        
        # This one change should be our new file
        path, path_hash, fingerprint, file_type, status = changes[0]
        self.assertTrue(path == self.new_file)
        self.assertTrue(file_type == FILE)
        self.assertTrue(status == ADDED)
        
        # After we commit, there should be no pending changes
        self.repository.commit()
        self.assertTrue(list(self.repository.iter_changes()) == [])
    
    def testDeleteFiles(self):
        """iter_changes should detect deleted files"""
        
        # Initialize a Repository, and then add and commit a new file
        self.testAddFiles()
        
        # Delete the new file
        os.remove(self.format_path(self.new_file))
        
        # Make sure that one change comes up in iter_changes
        changes = list(self.repository.iter_changes())
        self.assertTrue(len(changes) == 1)
        path, path_hash, fingerprint, file_type, status = changes[0]
        self.assertTrue(path == self.new_file)
        self.assertTrue(file_type == FILE)
        self.assertTrue(status == DELETED)
        
        # After we commit, there should be no pending changes
        self.repository.commit()
        self.assertTrue(list(self.repository.iter_changes()) == [])
    
    def testModifiedFiles(self):
        """iter_changes should detect modified files"""

        # Initialize a Repository, and then add and commit a new file
        self.testAddFiles()

        # Sleep a second so fingerprint of modified file will be different
        # (file modification time only has resolution in the order of one
        # to a few seconds)
        import time
        time.sleep(1)

        # Change that new file
        with open(self.format_path(self.new_file), 'w') as f:
            f.write("this is some amazing new content!")

        # Make sure that once change comes up in iter_changes
        changes = list(self.repository.iter_changes())
        self.assertTrue(len(changes) == 1)
        path, path_hash, fingerprint, file_type, status = changes[0]
        self.assertTrue(path == self.new_file)
        self.assertTrue(file_type == FILE)
        self.assertTrue(status == MODIFIED)

        # After we commit, there should be no pending changes
        self.repository.commit()
        self.assertTrue(list(self.repository.iter_changes()) == [])
        
    def testRevertUncommittedChanges(self):
        """revert should properly undo recent changes"""
        # Initialize a Repository, and then add and commit a new file
        self.testAddFiles()
        
        # No uncommitted changes should be sitting around
        self.assertTrue(list(self.repository.iter_changes()) == [])
        
        # Add another new file
        other_file = self.format_path("otherfile.txt")
        with open(other_file, 'w') as f:
            f.write("some other data")
        
        # Make sure file was created properly and is detected as a change
        self.assertTrue(os.path.exists(other_file))
        self.assertTrue(len(list(self.repository.iter_changes())) == 1)
        
        # Revert all uncommitted changes
        self.repository.revert()
        
        # Assert file no longer exists
        self.assertFalse(os.path.exists(other_file))
        self.assertTrue(list(self.repository.iter_changes()) == [])
        
        
    def testRevertLots(self):
        """revert should be able to undo all the way back to changset 1"""
        # Initialize a Repository and make a bunch of changes
        self.testModifiedFiles()
        
        # Revert all the way back to changeset 1
        self.repository.revert(changeset=1)
        
        # Assert all original files are present
        original_files = [x.split('->')[0] for x in self.test_files]
        for path in original_files:
            self.assertTrue(os.path.exists(self.format_path(path)))

        # Assert no other files are present
        ignored_patterns = self.repository.get_ignored_patterns()
        for root, dirs, files in os.walk(self.format_path('')):
            files = filter_all_patterns(files, ignored_patterns)
            for d in dirs:
                if matches_any_pattern(d, ignored_patterns):
                    dirs.remove(d)
            dirs = ["%s/" % d for d in dirs]
            for x in dirs + files:
                abspath = os.path.join(root, x)
                relpath = self.repository.get_relpath(abspath)
                self.assertTrue(relpath in original_files)
        
    def testPortability(self):
        """Checkpoint directories should continue working when moved."""
        # Initialize a Repository and commit the files
        self.testCommit()
        
        # Move the checkpoint directory
        old_temp_dir = self.temp_dir
        new_temp_dir = os.path.join(tempfile.gettempdir(), 'moved')
        os.chdir(tempfile.gettempdir()) # must leave a dir to move it
        os.rename(old_temp_dir, new_temp_dir)
        self.repository = Repository(new_temp_dir)
        
        # No changes were made, so no changes should be detected.
        changes = list(self.repository.iter_changes())
        self.assertTrue(len(changes) == 0)
        
        # Move stuff back so tearDown will still work
        os.rename(new_temp_dir, old_temp_dir)


class MirrorTest(TempFileTestCase):
    pass

if __name__ == "__main__":
    unittest.main()