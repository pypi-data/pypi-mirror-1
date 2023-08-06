"""Filesystem abstraction layer"""

import os
import shutil
import logging
import operator

from checkpoint.constants import FILE, LINK, DIRECTORY
from checkpoint.error import (
    FileError, NotFound, UnsupportedFileType, UninitializedRepositoryError
)
from checkpoint.util import ascending_length, descending_length

__all__ = ['FileStore']

log = logging.getLogger("checkpoint")

class FileStore(object):
    def __init__(self, repository_dir):
        self.data_path = self.__class__.get_data_path(repository_dir)
        self.metadata_path = self.__class__.get_metadata_path(repository_dir)

    @staticmethod
    def get_data_path(repository_dir):
        """Return the filestore path for a given repository."""
        return os.path.join(os.path.abspath(repository_dir), 'files')

    @staticmethod
    def get_metadata_path(repository_dir):
        """Return the filestore metadata path for a given repository."""
        return os.path.join(os.path.abspath(repository_dir), 'metadata')

    def initialize(self):
        """Create the filestore directories."""
        try:
            os.makedirs(self.data_path) 
            os.makedirs(self.metadata_path)
        except (OSError, IOError), e:
            raise FileError("Could not create filestore directory %r: %s" % 
                (self.path, e)
            )
            
    def is_initialized(self):
        """Quickly test whether a filestore has been initialized."""
        # Test if filestore directories exist
        if os.path.isdir(self.data_path) and os.path.isdir(self.metadata_path):
            return True
        else:
            return False
                
    def save(self, abspath, path_hash, fingerprint, file_type):
        """Save the specified path to the filestore."""
        log.debug("save path: %r, hash: %r, fingerprint: %r" % (
            abspath, path_hash, fingerprint
        ))
        # TODO: SHARDING!!! When you get too many files in a directory,
        # it starts taking a really long time to find the one you're looking
        # for.  Also some file systems have a maximum number of files 
        # that will fit in a directory:
        # FAT16: 512
        # FAT32: 65 thousand
        # NTFS: 4 billion

        try:
            # Store file data into repository
            data_destination = os.path.join(self.data_path, path_hash)
            if file_type == DIRECTORY:
                # Represent directories as empty files
                open(data_destination, 'w').close()
            elif file_type == LINK:
                # Represent links as files with the link target stored in them
                target = os.readlink(abspath)
                f = open(data_destination, 'w')
                f.write(target)
                f.close()
            elif file_type == FILE:
                # TODO: split file into 8k-128k chunks to de-duplicate
                # data.  See article on choosing a chunk size:
                # http://www.backupcentral.com/content/view/145/47/
                shutil.copy(abspath, data_destination)
            else:
                raise UnsupportedFileType()
                
            # For all file types, save the permission bits and access times
            metadata_destination = os.path.join(self.metadata_path, fingerprint)
            open(metadata_destination, 'w').close()
            shutil.copystat(abspath, metadata_destination)
        except (OSError, IOError), e:
            if not self.is_initialized():
                raise UninitializedRepositoryError()
            else:
                raise FileError("Error saving path %r: %s" % (abspath, e))

    def restore(self, abspath, path_hash, fingerprint, file_type):
        """Restore the specified path from the filestore.
        
        `abspath` - The absolute path where the file should be restored to.
        `path_hash` - The sha1 hash of the file in the filestore.
        `fingerprint` - The fingerprint of the file in the filestore.
        `file_type` - FILE, DIRECTORY, or LINK
        
        No attempt is made to create any necessary parent directories, and
        a FileError will be raised if the parent directory does not exist.

        """
        log.debug("restore path: %r, hash: %r" % (abspath, path_hash))
        # If destination path already exists, delete it
        try:
            self.delete(abspath)
        except NotFound:
            pass
        # Locate and restore the desired file from the filestore
        data_file = os.path.join(self.data_path, path_hash)
        metadata_file = os.path.join(self.metadata_path, fingerprint)
        for repository_file in [data_file, metadata_file]:
            if not os.path.isfile(repository_file):
                raise RepositoryError(
                    "Missing repository file %r" % repository_file
                )
        try:
            if file_type == DIRECTORY:
                os.mkdir(abspath)
            elif file_type == LINK:
                # Determine link target
                f = open(data_file)
                target = f.readline()
                f.close()
                # create target, if necessary (dependency problem workaround)
                if not os.path.exists(target):
                    open(target, 'w').close() # 'touch' file
                os.symlink(target, abspath)
            elif file_type == FILE:
                shutil.copy(data_file, abspath)
            # For all file types, restore the permission bits and access times
            shutil.copystat(metadata_file, abspath)
        except (OSError, IOError), e:
            raise FileError(
                "Error restoring path %r from repository: %s" % 
                (abspath, e)
            )

    def restore_multiple(self, path_infos):
        """Restore the specified files and directories from the filestore.

        `path_infos` must be a list of tuples like:
            (abspath, path_hash, fingerprint, file_type)

        Paths will be restored in the correct order to prevent dependency
        problems.  For example, directory '/a' will be restored before
        file '/a/b.txt' is restored.

        """
        path_infos.sort(cmp=ascending_length, key=operator.itemgetter(0))
        for abspath, path_hash, fingerprint, file_type in path_infos:
            self.restore(abspath, path_hash, fingerprint, file_type)
            
    @staticmethod
    def get_file_type(abspath):
        """Return the file type for path.

        Return value will be either LINK, FILE, DIRECTORY.

        An UnsupportedFileType error will be raised for unsupported file types
        such as pipes, sockets, and device files.

        A NotFound error will be raised if path does not exist.

        """
        if not os.path.lexists(abspath):
            raise NotFound(abspath)
        elif os.path.islink(abspath):
            return LINK
        elif os.path.isfile(abspath):
            return FILE
        elif os.path.isdir(abspath):
            return DIRECTORY
        else:
            raise UnsupportedFileType(abspath)

    def duplicate(self, source, destination, recurse=False):
        """Copy source (including stat info) to destination.
        
        DOES NOT modify the filestore in any way.
        
        A CheckpointError will be raised if destination already exists.
        A NotFound error will be raised if source does not exist.

        """
        file_type = self.get_file_type(source)
        if file_type == FILE:
            shutil.copy2(source, destination)
        elif file_type == LINK:
            target = os.readlink(source)
            os.symlink(target, destination)
        elif file_type == DIRECTORY:
            os.makedirs(destination)
            shutil.copystat(source, destination)

        if recurse and os.path.isdir(source):
            names = os.listdir(source)
            for name in names:
                next_source = os.path.join(source, name)
                next_destination = os.path.join(destination, name)
                self.duplicate(next_source, next_destination, recurse=True)
                    
    def delete(self, abspath):
        """Delete the specified path.
        
        DOES NOT modify the filestore in any way.
        
        A NotFound Exception will be raised if path does not exist.
        
        """
        if not os.path.exists(abspath):
            raise NotFound(abspath)
        file_type = self.get_file_type(abspath)
        try:
            if file_type == DIRECTORY:
                shutil.rmtree(abspath)
            elif file_type == FILE or file_type == LINK:
                os.remove(abspath)
            else: 
                raise UnsupportedFileType()
        except (OSError, IOError), e:
            raise FileError("Error deleting path %r: %s" % (abspath, e)) 

    def delete_multiple(self, paths):
        """Delete the specified files and directories.

        `paths` must be a list of absolute paths of files to delete.

        Paths will be deleted in the correct order to prevent dependency
        problems.  For example, file '/a/b.txt' will be deleted before
        directory '/a' is deleted.

        """
        paths.sort(cmp=descending_length)
        for path in paths:
            self.delete(path)