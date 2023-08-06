"""Unit-test the Checkpoint utilities"""

import os
import unittest

from checkpoint.tests.filestore import TempFileTestCase
from checkpoint.util import PickleProperty, acquire_lock, release_lock

__all__ = ['UtilityTest']

class UtilityTest(TempFileTestCase):
    def setUp(self):
        TempFileTestCase.setUp(self)
        
        # Create some files to test with
        self.create_temp_files(self.test_files)
    
    def testPickleProperty(self):
        """PickleProperty should work"""
        
        class Foo(object):
            bar = PickleProperty(lambda inst: getattr(inst, 'bar_data_file'))
            def __init__(inst):
                inst.bar_data_file = self.format_path('format')
        f = Foo()

        # Pickle file should exist after attribute access, and not before
        self.assertFalse(os.path.exists(f.bar_data_file))
        f.bar = "BAZ"
        self.assertTrue(os.path.exists(f.bar_data_file))
        
        # Data should come out of the pickle file correctly
        self.assertTrue(f.bar == "BAZ")

    def testFileLocks(self):
        """FileLocks should work"""

        class Locked(Exception):
            pass

        # Try to acquire a lock
        lockfile_path = self.format_path('lockfile')
        try:
            lock = acquire_lock(lockfile_path, Locked)
        except Locked, e:
            self.fail("Could not acquire lock")
        
        # Acquiring a lock while the old one is active should fail
        self.assertRaises(Locked, acquire_lock, lockfile_path, Locked)
        
        # Releasing a lock should work
        release_lock(lock)
        try:
            lock = acquire_lock(lockfile_path, Locked)
        except Locked, e:
            self.fail("Could not acquire lock after it was released")

if __name__ == "__main__":
    unittest.main()