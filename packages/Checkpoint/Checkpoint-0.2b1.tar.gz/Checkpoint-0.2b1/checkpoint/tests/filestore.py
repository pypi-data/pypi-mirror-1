"""Unit-test the Checkpoint FileStore"""

import os
import shutil
import errno
import hashlib
import tempfile
import unittest

from checkpoint.constants import FILE, DIRECTORY, LINK
from checkpoint.error import (
    UninitializedRepositoryError, UnsupportedFileType, NotFound
)
from checkpoint.util import descending_length
from checkpoint.filestore import FileStore

__all__ = ['TempFileTestCase', 'FileStoreTest']

class TempFileTestCase(unittest.TestCase):
    
    test_files = [
        "a.txt",
        "b.txt",
        "c.txt",
        "alink->a.txt", # link ('->' syntax only used in this test package)
        "morestuff/",
        "morestuff/d.txt",
        "morestuff/evenmore/",
        "morestuff/evenmore/e.txt"
    ]
    
    def format_path(self, unixpath):
        """Format a temp file path in the os-specific format."""
        return os.path.join(self.temp_dir, unixpath.replace('/', os.sep))
        
    def create_temp_files(self, paths):
        """Create the specified files and directories in the temp dir."""
        for path in paths:
            if '->' in path:
                # Create the specified link
                (link, target) = path.split('->')
                link = self.format_path(link)
                target = self.format_path(target)
                os.symlink(target, link)
            else:
                # Create the specified file or directory
                fullpath = self.format_path(path)
                if path.endswith('/'):
                    os.mkdir(fullpath)
                else:
                    f = open(fullpath, 'w')
                    f.write("TEST DATA!")
                    f.close()

    def setUp(self):
        """Prepare test environment (basic setup shared between all tests)."""
        # Determine temp directory to run tests in
        self.temp_dir = os.path.join(tempfile.gettempdir(), 'filestoretests')
        
        # Remove any stale files left over from previous tests
        try:
            shutil.rmtree(self.temp_dir)
        except OSError, e:
            if e.errno != errno.ENOENT:
                raise
            
        # Create temp dir and change to that directory
        os.mkdir(self.temp_dir)
        os.chdir(self.temp_dir)
        
    def tearDown(self):
        """Remove resources used by test environment."""
        os.chdir(self.temp_dir)
        os.chdir(os.pardir)
        shutil.rmtree(self.temp_dir)

class FileStoreTest(TempFileTestCase):
    def setUp(self):
        TempFileTestCase.setUp(self)
        
        # Create 'repository' dir
        self.repository = os.path.join(self.temp_dir, '.cpt')
        os.mkdir(self.repository)
        
        # Create some files to test with
        self.create_temp_files(self.test_files)
        
        # Create a FileStore object to test with
        self.filestore = FileStore(self.repository)
        
    def testKnownFileTypes(self):
        """get_file_type should work for supported file types."""
        for path in self.test_files:
            fullpath = self.format_path(path.split('->')[0])
            file_type = self.filestore.get_file_type(fullpath)
            if '->' in path:
                # Testing LINK
                self.assertEqual(file_type, LINK)
            elif path.endswith('/'):
                # Testing DIRECTORY
                self.assertEqual(file_type, DIRECTORY)
            else:
                # Testing FILE
                self.assertEqual(file_type, FILE)
    
    def testUnknownFileTypes(self):
        """Sockets and non-existant files should raise an error."""
        # Socket is not supported
        socketpath = self.format_path('mysocket')
        os.mkfifo(socketpath)
        self.assertRaises(
            UnsupportedFileType, self.filestore.get_file_type, socketpath
        )
        # Non-existant file
        notafile = self.format_path('SomePathThatsNotAFile')
        self.assertRaises(
            NotFound, self.filestore.get_file_type, notafile
        )
    
    def testRepositoryNotInitialized(self):
        """Uninitialized FileStores should raise an error on save()."""
        path = self.test_files[0] # any file will do
        fullpath = self.format_path(path.split('->')[0])
        some_hash = "000111" # any alpha-numeric data will do
        file_type = self.filestore.get_file_type(fullpath)
        self.assertRaises(
            UninitializedRepositoryError,
            self.filestore.save,
            fullpath,
            some_hash,
            some_hash,
            file_type
        )
    
    def testStoreFiles(self):
        """save should not raise an error."""
        self.filestore.initialize()
        for path in self.test_files:
            fullpath = self.format_path(path.split('->')[0])
            some_hash = hashlib.sha1(fullpath).hexdigest()
            file_type = self.filestore.get_file_type(fullpath)
            self.filestore.save(fullpath, some_hash, some_hash, file_type)

    def testDeleteFiles(self):
        """delete should actually delete files."""
        # Keep track of info for each path we will restore
        path_infos = []
        # Delete all files (deepest first to avoid dependency errors)
        deepest_first = self.test_files[:] # copy list
        deepest_first.sort(cmp=descending_length)
        for path in deepest_first:
            fullpath = self.format_path(path.split('->')[0])
            # Record info so we can restore files later
            some_hash = hashlib.sha1(fullpath).hexdigest()
            file_type = self.filestore.get_file_type(fullpath)
            path_infos.append(
                (fullpath, some_hash, some_hash, file_type)
            )
            # Delete path and assert it's not there anymore
            self.filestore.delete(fullpath)
            self.assertFalse(os.path.exists(fullpath))
        return path_infos

    def testRestoreFiles(self):
        """restore_multiple should correctly restore deleted files."""
        # Initialize filestore and save all test files
        self.testStoreFiles()
        # Delete those test files, so we can restore them in a moment
        path_infos = self.testDeleteFiles()
        # Restore all files and assert they exist once more
        self.filestore.restore_multiple(path_infos)
        for path in self.test_files:
            fullpath = self.format_path(path.split('->')[0])
            self.assertTrue(os.path.exists(fullpath))

if __name__ == "__main__":
    unittest.main()