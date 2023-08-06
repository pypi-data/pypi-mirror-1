"""File System abstraction layer"""

import os
import shutil
import logging
import operator

from checkpoint.error import *
from checkpoint.util import ascending_length, descending_length

__all__ = ['FileStore', 'FILE', 'DIRECTORY', 'LINK']

log = logging.getLogger("checkpoint")

FILE = 0
DIRECTORY = 1
LINK = 2

class FileStore(object):
    def __init__(self, repository_dir):
        super(FileStore, self).__init__()        
        self.path = self.__class__.get_path(repository_dir)

    @staticmethod
    def get_path(repository_dir):
        """Return the filestore path for a given repository."""
        return os.path.join(os.path.abspath(repository_dir), 'files')

    def initialize(self):
        """Create the filestore directory."""
        try:
            os.makedirs(self.path)
        except (OSError, IOError), e:
            raise FileError("Could not create filestore %r: %s" % 
                (self.path, e)
            )

    @staticmethod
    def get_file_type(path):
        """Return the file type for path.
        
        Return value will be either LINK, FILE, DIRECTORY.
        
        An UnsupportedFileType error will be raised for unsupported file types
        such as pipes, sockets, and device files.
        
        A NotFound error will be raised if path does not exist.
        
        """
        if not os.path.lexists(path):
            raise NotFound(path)
        elif os.path.islink(path):
            return LINK
        elif os.path.isfile(path):
            return FILE
        elif os.path.isdir(path):
            return DIRECTORY
        else:            
            raise UnsupportedFileType(path)

    def save(self, path, path_hash, file_type):
        """Save the specified path to the filestore."""
        log.debug("save path: %r, hash: %r" % (path, path_hash))
        destination = os.path.join(self.path, path_hash)
        try:
            if file_type == DIRECTORY:
                # Represent directories as empty files
                open(destination, 'w').close()
            elif file_type == LINK:
                # Represent links as files with the link target stored in them
                f = open(destination, 'w')
                f.write(os.path.realpath(path))
                f.close()
            elif file_type == FILE:
                shutil.copy(path, destination)
            # For all file types, save the permission bits and access times
            shutil.copystat(path, destination)
        except (OSError, IOError), e:
            raise FileError(
                "Error saving path %r into repository file %r: %s" %
                (path, destination, e)
            )
    
    def save_multiple(self, paths):
        """Save the specified files and directories into the filestore"""
        for p in paths:
            self.save(paths)

    def restore(self, path, path_hash, file_type):
        """Restore the specified path from the filestore.
        
        No attempt is made to create any necessary parent directories, and
        a FileError will be raised if the parent directory does not exist.

        """
        log.debug("restore path: %r, hash: %r" % (path, path_hash))
        # If destination path already exists, delete it
        try:
            self.delete(path)
        except NotFound:
            pass
        # Locate and restore the desired file from the filestore
        filestore_file = os.path.join(self.path, path_hash)
        if not os.path.isfile(filestore_file):
            raise RepositoryError(
                "Missing repository file %r" % repository_file
            )
        try:
            if file_type == DIRECTORY:
                os.mkdir(path)
            elif file_type == LINK:
                # Determine link target
                f = open(filestore_file)
                target = f.readline()
                f.close()
                os.symlink(target, path)
            elif file_type == FILE:
                shutil.copy(filestore_file, path)
            # For all file types, restore the permission bits and access times
            shutil.copystat(filestore_file, path)
        except (OSError, IOError), e:
            raise FileError(
                "Error restoring path %r from repository file %r: %s" % 
                (path, filestore_file, e)
            )

    def restore_multiple(self, path_infos):
        """Restore the specified files and directories from the filestore.

        `path_infos` must be a list of (path, path_hash, file_type) tuples

        Paths will be restored in the correct order to prevent dependency
        problems.  For example, directory '/a' will be restored before
        file '/a/b.txt' is restored.

        """
        path_infos.sort(cmp=ascending_length, key=operator.itemgetter(0))
        for path, path_hash, file_type in path_infos:
            self.restore(path, path_hash, file_type)
            
    def delete(self, path):
        """Delete the specified path.
        
        A NotFound Exception will be raised if path does not exist.
        
        No attempt is made to empty directories, and a FileError will be
        raised if an attempt is made to delete a non-empty directory.
        
        """
        if not os.path.exists(path):
            raise NotFound(path)
        file_type = self.get_file_type(path)
        try:
            if file_type == DIRECTORY:
                os.rmdir(path)
            else:
                os.remove(path)
        except (OSError, IOError), e:
            raise FileError("Error deleting path %r: %s" % (path, e))

    def delete_multiple(self, paths):
        """Delete the specified files and directories.

        Paths will be deleted in the correct order to prevent dependency
        problems.  For example, file '/a/b.txt' will be deleted before
        directory '/a' is deleted.

        """
        paths.sort(cmp=descending_length)
        for path in paths:
            self.delete(path)