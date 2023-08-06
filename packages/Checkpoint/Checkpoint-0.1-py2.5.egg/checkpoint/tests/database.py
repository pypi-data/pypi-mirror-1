"""Unit-test the Checkpoint Database system"""

import os
import shutil
import errno
import tempfile
import unittest

from checkpoint.error import *
from checkpoint.database import Database
from checkpoint.filestore import FILE, LINK, DIRECTORY
from checkpoint.repository import ADDED, DELETED

__all__ = ['DatabaseTest']

class DatabaseTest(unittest.TestCase):
    def setUp(self):
        """Prepare test environment (basic setup shared between all tests)."""
        # Determine temp directory to run tests in
        self.temp_dir = os.path.join(tempfile.gettempdir(), 'databasetests')
        
        # Remove any stale files left over from previous tests
        try:
            shutil.rmtree(self.temp_dir)
        except OSError, e:
            if e.errno != errno.ENOENT:
                raise
            
        # Create temp dir and change to that directory
        os.mkdir(self.temp_dir)
        os.chdir(self.temp_dir)

        # Create 'repository' dir
        self.repository = os.path.join(self.temp_dir, '.cpt')
        os.mkdir(self.repository)
        
        # Create a FileStore object to test with
        self.db = Database(self.repository)
        
    def tearDown(self):
        """Remove resources used by test environment."""
        os.chdir(self.temp_dir)
        os.chdir(os.pardir)
        shutil.rmtree(self.temp_dir)

    def testRepositoryNotInitialized(self):
        """Uninitialized Databases should raise an error on access."""
        self.assertRaises(
            UninitializedRepositoryError, self.db.select, 'modifications'
        )

    def testInsert(self):
        """INSERTs should work."""
        # Initialize database (create tables, etc)
        self.db.initialize()
        # Assert table starts out empty
        self.assertFalse(self.db.select('changeset').fetchone())
        # Do a test insertion
        new_changeset = self.db.insert('changeset', dict(id=None)).lastrowid
        # Assert table now has a record in it
        self.assertTrue(self.db.select('changeset').fetchone())
        # Assert new changeset has a valid integer id
        self.assertTrue(new_changeset is not None)
        # Return the new changeset for other tests to use
        return new_changeset
        
    def testGetCurrentChangeset(self):
        """get_current_changeset should return the latest changeset id."""
        # Initialize DB and create a changeset to work with
        new_changeset = self.testInsert()
        # Assert this changeset comes back to us as the latest changeset.
        self.assertTrue(self.db.get_current_changeset() == new_changeset)
        
    def testRecordPaths(self):
        """record_added should work."""
        # test data -- path, hash, fingerprint, file_type, status
        self.path_infos = [
            ('/path/a.txt', 'test-hash-1', 'test-hash-2', FILE, ADDED),
            ('/path/b.txt', 'test-hash-3', 'test-hash-4', LINK, ADDED),
            ('/path/more', 'test-hash-5', 'test-hash-6', DIRECTORY, ADDED)
        ]
        # Initialize DB and create a changeset to work with
        new_changeset = self.testInsert()
        # Save our test data into the database
        for x in self.path_infos:
            self.db.record_added(new_changeset, *x)
        # Assert the test data was saved correctly.
        for x in self.path_infos:
            results = self.db.select('modification',
                ['hash', 'fingerprint', 'type', 'status'],
                dict(path=x[0])
            ).fetchone()
            self.assertTrue(results == x[1:])
        # Test the get_active_* methods
        for x in self.path_infos:
            self.assertTrue(self.db.get_active_hash(x[0]) == x[1])
            self.assertTrue(self.db.get_active_fingerprint(x[0]) == x[2])
            self.assertTrue(self.db.get_active_file_type(x[0]) == x[3])

    def testPathDeletions(self):
        """record_deleted should work."""
        self.testRecordPaths()
        # Make a new changeset for these changes
        new_changeset = self.db.insert('changeset', dict(id=None)).lastrowid
        # Do a 'deletion' for all test paths
        for x in self.path_infos:
            data = list(x[:-1]) + [DELETED]
            self.db.record_deleted(new_changeset, *data)
        # Assert the deletions saved correctly
        for x in self.path_infos:
            data = list(x[:-1]) + [DELETED]
            results = self.db.select('modification',
                ['hash', 'fingerprint', 'type', 'status'],
                dict(path=data[0], status=DELETED)
            ).fetchone()
            self.assertTrue(list(results) == list(data[1:]))
    
    def testGetPreviousVersion(self):
        """get_previous_version should work"""
        # Record path additions and deletions
        self.testPathDeletions()
        # Determine current changeset
        changeset = self.db.get_current_changeset()
        # For each test path, assert previous version has status=ADDED
        for x in self.path_infos:
            path = x[0]
            results = self.db.get_previous_version(path, changeset)
            self.assertTrue(list(results) == list(x[1:]))

if __name__ == "__main__":
    unittest.main()