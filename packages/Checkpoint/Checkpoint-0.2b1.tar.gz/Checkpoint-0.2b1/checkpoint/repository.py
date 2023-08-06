"""Checkpoint repository management"""

from __future__ import with_statement

import os
import shutil
import hashlib
import logging
from textwrap import dedent

from checkpoint.constants import (
    NO_CHANGE, ADDED, DELETED, MODIFIED, FILE, DIRECTORY, LINK, RAISE_ERR
)
from checkpoint.database import Database
from checkpoint.filestore import FileStore
from checkpoint.error import (
    RepositoryLocked, FileError, UninitializedRepositoryError, CheckpointBug,
    RepositoryError, NoChanges, UnsupportedFileType, NotFound, MirrorLocked,
    UninitializedMirrorError, CheckpointError
)
from checkpoint.util import (
    acquire_lock, release_lock, PickleProperty, filter_all_patterns,
    matches_any_pattern, sha1_hash, filter_duplicates
)

__all_ = [
    'Repository', 'STATUS_CODES', 'DEFAULT_REPOSITORY_BASENAME', 
    'SUPPORTED_REPOSITORY_FORMAT'
]

log = logging.getLogger("checkpoint")
#logging.basicConfig(level=logging.DEBUG)

DEFAULT_REPOSITORY_BASENAME = '.cpt'
SUPPORTED_REPOSITORY_FORMAT = "1" # format supported by this release

STATUS_CODES = {
    NO_CHANGE: '',
    ADDED: 'A',
    DELETED: 'D',
    MODIFIED: 'M',
}

# Notes on relative/absolute paths:
#   * All methods and functions in this module accept relative paths ONLY.
#   * Also, all methods in the Database module use relative paths only.
#   * The FileStore methods on the other hand, use only absolute paths.

class Common(object):
    """Common functionality for Repository and Mirror classes"""
    
    @staticmethod
    def get_repository_basename():
        """Return the basename (default '.cpt') for the repository."""
        basename = DEFAULT_REPOSITORY_BASENAME
        try:
            basename = os.environ['CHECKPOINT_REPOSITORY_BASENAME']
        except KeyError:
            pass 
        return basename

    @classmethod
    def get_repository_path(cls, directory):
        """Return the absolute repository path for a given directory."""
        # Determine repository path
        basename = cls.get_repository_basename()
        directory = os.path.abspath(directory)
        return os.path.join(directory, basename)

    @classmethod
    def get_ignored_patterns(cls):
        """Determine the basename patterns (ex: '*.jpg') to ignore."""
        # Always ignore repositories
        ignored_patterns = [cls.get_repository_basename()]
        # Check for additional patterns specified by environment variables
        try:
            ignored_patterns.extend(
                os.environ['CHECKPOINT_IGNORED_PATTERNS'].split(':')
            )
        except KeyError:
            pass
        return ignored_patterns

class Mirror(Common):
    """Checkpoint Repository Mirror.
    
    This is an *incredibly* fast and efficient mirroring process that uses 
    the mirrored repository's database of changes in order to minimize the
    number of file system operations needed to mirror the repository.
    
    """
    
    # Use PickleProperty's to load/save the state of the mirror
    source_directory = PickleProperty(
        lambda inst: os.path.join(
            os.path.abspath(inst.config_directory), 
            'mirror_path'
        )
    )
    changeset = PickleProperty(
        lambda inst: os.path.join(
            os.path.abspath(inst.config_directory), 
            'changeset'
        )
    )

    def __init__(self, destination_directory):
        # Determine paths for the mirror directory
        self.destination_directory = os.path.abspath(destination_directory)
        self.config_directory = Mirror.get_repository_path(
            self.destination_directory
        )
        self.lockfile_path = os.path.join(self.config_directory, 'lock')
        
        # Create destination and config directories, as needed.
        for d in [self.destination_directory, self.config_directory]:
            if not os.path.exists(d):
                try:
                    os.makedirs(d)
                except (OSError, IOError), e:
                    raise FileError(
                        "Could not create mirror directory %r: %s" % (d, e)
                    )
        # Create database
        self.db = Database(self.config_directory)
    
    @staticmethod
    def contains_mirror(directory):
        """Returns True if directory contains a Mirror, False otherwise."""
        if directory is None: return False
        some_mirror_file = os.path.join(
            Mirror.get_repository_path(directory),
            'mirror_path'
        )
        if os.path.exists(some_mirror_file):
            return True
        else:
            return False

    def lock(method):
        """Return decorator that locks the mirror while method is running."""
        def wrapper(self, *args, **kwargs):
            # Acquire a lock
            lock = acquire_lock(self.lockfile_path, MirrorLocked)
            try:
                # Call the decorated method
                return_value = method(self, *args, **kwargs)
            finally:
                # Release the lock
                release_lock(lock)
            # Return the method results
            return return_value
        return wrapper

    def require_mirror(method):
        """Decorator that raises an error if mirror doesn't exist."""
        def wrapper(self, *args, **kwargs):
            if not Mirror.contains_mirror(self.destination_directory):
                raise UninitializedMirrorError()
            else:
                return method(self, *args, **kwargs)
        return wrapper

    @require_mirror
    def delete_mirror(self):
        """Completely delete the mirror."""
        log.info(
            "Deleting mirror for directory %r" % self.destination_directory
        )
        # Delete mirror config stuff, leaving the directory untouched
        try:
            shutil.rmtree(self.config_directory)
        except (OSError, IOError), e:
            raise FileError("Error deleting mirror %r: %s" % 
                (self.config_directory, e)
            )

    def mirror(self, source_directory):
        """Create a mirror of the specified Checkpoint directory."""
        # Start a database transaction that will rollback on Exception
        with self.db:
            return self.__mirror(source_directory)

    def __mirror(self, source_directory):
        """See mirror() for details."""
        
        # Determine path to the source directory, and save this
        # configuration data to the filesystem (thanks to a PickleProperty).
        self.source_directory = os.path.abspath(source_directory)

        log.info(
            "Initializing mirror of directory: %r" % self.source_directory
        )

        # Instantiate a Repository object pointed at the source directory
        self.source_repository = Repository(self.source_directory)

        # Initialize db
        self.db.initialize()

        # Assert that the source repository has been initialized
        if not Repository.contains_repository(self.source_directory):
            raise UninitializedRepositoryError()
        
        # Mirror the repository's active set of files and properties
        mirrored_changeset = self.source_repository.current_changeset
        active_set = self.source_repository.db.select('active_set', 
            columns=['path', 'hash', 'fingerprint', 'type']
        )
        for relpath, path_hash, fingerprint, file_type in active_set:
            log.info("%s\t%s" % (STATUS_CODES[ADDED], relpath))
            # Mirror the file/dir/link
            self.source_repository.filestore.restore(
                self.get_abspath(relpath), 
                path_hash, 
                fingerprint, 
                file_type
            )
            # Mirror all properties for this file/dir/link
            active_properties = self.db.iterate_properties(
                relpath, mirrored_changeset
            )
            for propname, propval in active_properties:
                self.db.set_property(
                    propname, propval, relpath, mirrored_changeset
                )
        
        # Record the currently-mirrored changeset
        self.changeset = mirrored_changeset
        log.info("Current changeset: %s" % self.changeset)

    def get_abspath(self, relpath):
        """Return the absolute path to relpath in the mirror directory."""
        return os.path.abspath(
            os.path.join(self.destination_directory, relpath)
        )
    
    @require_mirror
    @lock
    def refresh(self):
        """Mirror the source repository."""
        with self.db:
            return self.__refresh()

    def __refresh(self):
        """See refresh() for details."""

        # Instantiate a Repository object pointed at the source directory
        # Note: self.source_directory is a PickleProperty
        self.source_repository = Repository(self.source_directory)

        # Assert that the source repository has been initialized
        if not Repository.contains_repository(self.source_directory):
            raise UninitializedRepositoryError()

        # Iterate through changesets committed since the last 'refresh'
        change_count = 0
        start = self.changeset + 1
        end = self.source_repository.current_changeset + 1
        for mod_changeset in range(start, end):
            additions = []
            deletions = []
            modifications = []
            
            # Iterate through property changes in this changeset
            property_changes = self.source_repository.db.select(
                'property',
                columns=['propname', 'propval', 'path', 'status'],
                where_clauses=dict(changeset_id=mod_changeset)
            )
            for change in property_changes:
                # Unpack data in the 'change' tuple
                propname, propval, path, status = change
                # Delete any pre-existing property values
                self.db.delete(
                    'property', dict(propname=propname, path=path)
                )
                if status in [MODIFIED, ADDED]:
                    # Insert current property value into database
                    new_prop = {
                        'path': path,
                        'changeset_id': mod_changeset,
                        'propname': propname,
                        'propval': propval,
                        'status': status
                    }
                    self.db.insert('property', new_prop)
                elif status == DELETED:
                    # Property value was already deleted, nothing to do here.
                    pass
                else:
                    raise CheckpointBug(
                        "Invalid modification status: %r" % status
                    )
                    
            # Iterate through path changes in this changeset
            path_changes = self.source_repository.db.select(
                'modification', 
                columns=[
                    'changeset_id', 'path', 'hash', 'fingerprint', 'type', 
                    'status'
                ],
                where_clauses=dict(changeset_id=mod_changeset)
            )
            for change in path_changes:
                # Unpack data in the 'change' tuple
                (mod_changeset, relpath, path_hash, 
                fingerprint, file_type, status) = change
                # Determine path to target file in mirror directory
                target_path = self.get_abspath(relpath)
                # Log what's happening
                change_count += 1
                log.info("%s\t%s" % (STATUS_CODES[status], relpath))
                # Add change to the appropriate list
                if status == ADDED:
                    additions.append(
                        (target_path, path_hash, fingerprint, file_type)
                    )
                elif status == DELETED:
                    deletions.append(target_path)
                elif status == MODIFIED:
                    modifications.append(
                        (target_path, path_hash, fingerprint, file_type)
                    )
                else:
                    raise CheckpointBug(
                        "Invalid modification status: %r" % status
                    )
            # Perform all file changes
            self.source_repository.filestore.restore_multiple(modifications)
            self.source_repository.filestore.restore_multiple(additions)
            self.source_repository.filestore.delete_multiple(deletions)
            
            # Record the currently-mirrored changeset
            self.changeset = self.source_repository.current_changeset
            log.info("Current changeset: %s" % self.changeset)
    
    @require_mirror
    def get_property(self, propname, path, default=RAISE_ERR):
        """Get the property value for the specified relative path."""
        propval = self.db.get_property(propname, path, default)
        log.info("\t%s" % propval)
        return propval
    
    @require_mirror
    def iterate_properties(self, path):
        """Return an iterator of properties on the specified relative path.
        
        Yields properties as (propname, propval) tuples.
        
        """
        return self.db.iterate_properties(path)

    @require_mirror
    def recover(self):
        """Attempt to re-mirror the directory"""
        try:
            self.__recover()
        except:
            log.info(dedent("""
                --------------------------------------------------------------
                !!! Recovery Failed! !!!

                Checkpoint failed to restore mirror %r.

                Further error messages may indicate the source of the failure.

                Manual crash-recovery may be the only option.  
                Check the documentation for more information.
                --------------------------------------------------------------

            """ % (self.destination_directory)
            ))
            raise

    def __recover(self):
        """Attempt to delete and re-mirror the mirror."""
        source_directory = self.source_directory
        self.delete_mirror()
        self.mirror(source_directory)
        # Delete any lockfiles
        if os.path.exists(self.lockfile_path):
            try:
                os.remove(self.lockfile_path)
            except (OSError, IOError), e:
                raise FileError(
                    "Could not remove lockfile %r:  %s" % 
                    (self.lockfile_path, e)
                )
        
class Repository(Common):
    """Checkpoint Repository"""

    # Use a PickleProperty to load/save the repository format number    
    repository_format = PickleProperty(
        lambda inst: os.path.join(
            os.path.abspath(inst.repository_path), 
            'repository_format'
        )
    )
    
    def __init__(self, directory):
        """Initialize a repository in the specified directory."""
        # Raise error if directory has not been created
        if not os.path.isdir(directory):
            raise NotFound("Could not find directory %r" % directory)
        
        self.directory = os.path.abspath(directory) # directory to 'watch'
        self.repository_path = Repository.get_repository_path(self.directory)
        self.db = Database(self.repository_path)
        self.filestore = FileStore(self.repository_path)
        self.lockfile_path = os.path.join(self.repository_path, 'lock')

    def initialize(self):
        """Initialize the repository. Used by the `watch` command."""
        log.info("Initializing repository for directory: %r" % self.directory)

        # Create repository directory and crash-recovery directory
        try:
            os.makedirs(self.repository_path)
        except (OSError, IOError), e:
            raise FileError("Could not create repository %r: %s" % 
                (self.repository_path, e)
            )

        # Record the supported repository format
        self.repository_format = SUPPORTED_REPOSITORY_FORMAT

        # Initialize db and filestore
        self.db.initialize()
        self.filestore.initialize()

    @staticmethod
    def contains_repository(directory):
        """Return True if directory contains a Repository, False otherwise."""
        some_repository_file = os.path.join(
            Repository.get_repository_path(directory),
            'repository_format'
        )
        if os.path.exists(some_repository_file):
            return True
        else:
            return False

    def lock(method):
        """Return decorator that locks repository while method is running."""
        def wrapper(self, *args, **kwargs):
            # Acquire a lock
            lock = acquire_lock(self.lockfile_path, RepositoryLocked)
            try:
                # Call the decorated method
                return_value = method(self, *args, **kwargs)
            finally:
                # Release the lock
                release_lock(lock)
            # Return the method results
            return return_value
        return wrapper

    def require_repository(method):
        """Decorator that raises an error if repository wasn't initialized."""
        def wrapper(self, *args, **kwargs):
            if not Repository.contains_repository(self.directory):
                raise UninitializedRepositoryError()
            else:
                return method(self, *args, **kwargs)
        return wrapper

    def __get_current_changeset(self):
        """Return the last committed changeset id."""
        return self.db.current_changeset
    current_changeset = property(__get_current_changeset)

    def get_relpath(self, abspath):
        """Return the relative path to abspath to the Checkpoint directory."""
        return os.path.normpath(abspath[len(self.directory):].lstrip(os.sep))

    def get_abspath(self, relpath):
        """Return the absolute path to relpath in the Checkpoint directory."""
        return os.path.normpath(
            os.path.abspath(os.path.join(self.directory, relpath))
        )

    def get_fingerprint(self, relpath):
        """Return a fingerprint to help determine if path has been changed."""
        # Determine file type (link, directory, file)
        abspath = self.get_abspath(relpath)
        file_type = self.filestore.get_file_type(abspath)
        
        # Create the hash for this fingerprint, starting with 'relpath' data
        h = hashlib.sha1()
        h.update(unicode(relpath))
        
        # Use 'lstat' to get additional fingerprint info
        try:
            stat_info = os.lstat(abspath)
        except (OSError, IOError), e:
            raise FileError(
                "Could not determine status of file %r: %s" % (relpath, e)
            )
            
        # Update the hash with specific file data
        if file_type == FILE or file_type == LINK:
            for k in ['st_mode', 'size', 'st_mtime', 'st_flags']:
                if hasattr(stat_info, k):
                    h.update(str(getattr(stat_info, k)))
            return h.hexdigest()
        elif file_type == DIRECTORY:
            h.update(str(stat_info.st_mode))
            return h.hexdigest()
        else:
            raise UnsupportedFileType(abspath)

    def get_modification_status(self, relpath):
        """Return the modification status of the given file or directory.

        For files and directories that exist currently in the Checkpoint
        directory, determine if file or directory was newly ADDED or 
        newly MODIFIED, and return the corresponding constant.  For files and 
        directories that do not currently exist on the file system, look in 
        the database to determine if the file or directory was recently 
        DELETED.  If the file or directory has not changed since the last 
        commit, then NO_CHANGE is returned.

        """
        # Determine file type, catching NotFound error for nonexistant files
        # but letting UnsupportedFileType errors bubble up.
        abspath = self.get_abspath(relpath)
        try:
            file_type = self.filestore.get_file_type(abspath)
        except NotFound:
            pass
        exists_in_filesystem = os.path.lexists(abspath)
        exists_in_db = self.db.exists('active_set', dict(path=relpath))

        # If path is not in database, assume it was recently ADDED.
        if not exists_in_db:
            return ADDED

        # If path exists in the database but not in the filesystem,
        # assume it was recently DELETED.
        if exists_in_db and not exists_in_filesystem:
            return DELETED

        # If path exists in the database and in the filesystem,
        # test path to see if it was recently MODIFIED.
        if exists_in_db and exists_in_filesystem:
            fingerprint = self.get_fingerprint(relpath)
            original_fingerprint = self.db.get_active_fingerprint(relpath)
            if unicode(original_fingerprint) == unicode(fingerprint):
                return NO_CHANGE
            else:
                return MODIFIED

    @require_repository
    def delete_repository(self):
        """Completely delete the repository."""
        log.info("Deleting repository for directory %r" % self.directory)
        # Delete repository, leaving the 'watched' directory untouched
        try:
            shutil.rmtree(self.repository_path)
        except (OSError, IOError), e:
            raise FileError("Error deleting repository %r: %s" % 
                (self.repository_path, e)
            )

    @require_repository
    @lock
    def copy(self, source, destination):
        """Duplicate something in a Checkpoint directory.
        
        `source` and `destination` must be specified as relative paths.
        
        This uses shutil.copy2 to copy data and stat info ("cp -p src dst").
        
        A CheckpointError will be raised if `destination` already exists,
        or if `source` doesn't exist or has uncommitted modifications.
        
        """
        self.__copy(source, destination)

    def __copy(self, source, destination):
        """See copy() for details."""
        abs_source = self.get_abspath(source)
        abs_destination = self.get_abspath(destination)
        # If destination is a directory, source file/dir should be copied
        # INTO the destination directory, not OVERWRITING it.
        if os.path.isdir(abs_destination):
            abs_destination = os.path.join(
                abs_destination,
                os.path.split(source)[-1]
            )

        # Raise an error if source doesn't exist
        if not os.path.lexists(abs_source):
            raise NotFound(source)

        # Raise an error if destination exists
        if os.path.lexists(abs_destination):
            raise CheckpointError(
                "Destination path %r already exists" % destination
            )

        # Raise an error if destination is inside source
        if os.path.isdir(abs_source):
            test_path = abs_destination
            while True:
                if test_path == abs_source:
                    raise CheckpointError(
                        "Destination %r cannot be inside source %r" %
                        (destination, source)
                    )
                test_parent = os.path.dirname(test_path)
                if test_parent == test_path:
                    break
                else:
                    test_path = test_parent

        # Wrap the database changes in a transaction
        with self.db:
            try:
                # Walk `source` and copy everything to `destination`
                for s in self.walk(source):
                    # Unpack information about each source path
                    relpath, abspath, fingerprint, file_type, status = s
                    # Raise an error if source has uncommitted modifications
                    if status != NO_CHANGE:
                        raise CheckpointError(
                            "Path %r has unsaved modifications, commit first" %
                            source
                        )
                    # Duplicate this path
                    rel_dest = abspath[len(abs_source):].rstrip(os.sep)
                    if rel_dest:
                        abs_dup_path = os.path.join(abs_destination, rel_dest)
                    else:
                        abs_dup_path = abs_destination
                    rel_dup_path = self.get_relpath(abs_dup_path)
                    self.filestore.duplicate(abspath, abs_dup_path)
                    # Duplicate properties
                    props = self.db.iterate_properties(
                        relpath, self.current_changeset
                    )
                    for propname, propval in props:
                        self.db.set_property(propname, propval, rel_dup_path)
                    # Log an addition for 'destination'
                    log.info("%s\t%s" % (STATUS_CODES[ADDED], rel_dest))
            except:
                # Error! Delete the partial copy (if it exists)
                if os.path.exists(abs_destination):
                    self.filestore.delete(abs_destination)
                # Re-raise exception, which also happens to rollback the
                # db changes thanks to the db context manager.
                raise

    @require_repository
    @lock
    def move(self, source, destination):
        """Move/Rename file and its associated properties.
        
        `source` and `destination` must be specified as relative paths.
        
        A CheckpointError will be raised if `destination` already exists, or
        if `source` has uncommitted modifications.
        
        """
        # Copy `source` to `destination`, raising an exception if
        # `destination` exists or if `source` has uncommitted modifications.
        self.__copy(source, destination)
        
        # Delete `source` from the filesystem
        abs_source = self.get_abspath(source)
        self.filestore.delete(abs_source)
        
        # Log a deletion for `source`
        log.info("%s\t%s" % (STATUS_CODES[DELETED], source))
    
    @require_repository
    @lock
    def delete_property(self, propname, path):
        """Delete a property from the specified relative path."""
        with self.db:
            self.db.delete_property(propname, path)
        log.info("Property %r deleted from %r" % (propname, path))
    
    @require_repository
    @lock
    def get_property(self, propname, path, default=RAISE_ERR):
        """Get the property value for the specified relative path."""
        propval = self.db.get_property(propname, path, default)
        log.info("\t%s" % propval)
        return propval
    
    @require_repository
    @lock
    def iterate_properties(self, path):
        """Return an iterator of properties on the specified relative path.
        
        Yields properties as (propname, propval) tuples.
        
        """
        return self.db.iterate_properties(path)
    
    @require_repository
    @lock
    def set_property(self, propname, propval, path):
        """Set a property value on the specified relative path."""
        with self.db:
            self.db.set_property(propname, propval, path)
        log.info("Property %r set on %r" % (propname, path))
    
    @require_repository
    @lock
    def iterate_changes(self, paths=None):
        """Return an iterable of repository changes since the last commit.
        
        Optionally, a list of relative paths may be specified, and then the
        results will only include changes to those paths. For each directory
        specified in this list of paths, that directory will be walked
        recursively to find changes.
        
        Each item returned will be a tuple containing these fields:
            `path` - path to the changed file (relative to 'watched' directory)
            `path_hash` - sha1 hash of the changed file
                for MODIFIED or ADDED files, this is a hash of the current file
                for DELETED files, this is the hash of the old file
            `fingerprint` - sha1 hash of various stat() data, used to 
                quickly detect if the file has changed or not
            `file_type` - FILE, DIRECTORY, or LINK
            `status` - ADDED, DELETED, or MODIFIED

        Results are not sorted in any way, and the order of yield-ed
        results should not be relied on for any particular purpose.

        Special files (pipes, sockets, etc) are ignored.

        Paths that were renamed or moved will be detected as one path being 
        deleted and another path being added.
        
        """
        # This method is merely a @lock-ed version of self.__iterate_changes
        for change in self.__iterate_changes(paths=paths):
            yield change

    def __iterate_changes(self, paths=None):
        """See iterate_changes() for details."""
        # If paths were not specified, return all changes
        if paths is None:
            for change in self.__iterate_all_changes():
                yield change
        # However if paths were specified, filter the result set accordingly
        else:
            filter_patterns = []
            for path in paths:
                abspath = self.get_abspath(path)
                if os.path.isdir(abspath):
                    filter_patterns.append("%s*" % path)
                else:
                    filter_patterns.append(path)
            for change in self.__iterate_all_changes():
                (relpath, path_hash, fingerprint, file_type, status) = change
                if matches_any_pattern(relpath, filter_patterns):
                    yield change

    def __iterate_all_changes(self):
        """Same as __iterate_changes() but without any path filtering."""
        # Iterate through the 'active_set' database table (which stores the 
        # state of all files at the time of the last commit), and see if any 
        # of those files or directories have been DELETED
        active_set = self.db.select('active_set', 
            columns=['path', 'hash', 'fingerprint', 'type']
        )
        yielded_paths = []
        for relpath, path_hash, fingerprint, file_type in active_set:
            try:
                status = self.get_modification_status(relpath)
            except UnsupportedFileType, e:
                log.warning(e.message)
            else:
                if status == DELETED:
                    yielded_paths.append(relpath)
                    yield (relpath, path_hash, fingerprint, file_type, status)
        
        # Walk directory and yield files and directories that 
        # were ADDED or MODIFIED since the last commit
        for relpath, abspath, fingerprint, file_type, status in self.walk():
            # Yield any files/dirs that have been ADDED or MODIFIED
            if status == ADDED or status == MODIFIED:
                path_hash = sha1_hash(abspath)
                yielded_paths.append(relpath)
                yield (
                    relpath, path_hash, fingerprint, file_type, status
                )

        # Iterate through uncommitted property changes, and yield them
        # if that path hasn't been yielded already.
        ignored_patterns = self.get_ignored_patterns()
        results = self.db.select('property', ['path'], {'changeset_id': None})
        for (relpath,) in results:
            if ((relpath not in yielded_paths) and
                (not matches_any_pattern(relpath, ignored_patterns))):
                path_hash = self.db.get_active_hash(relpath)
                fingerprint = self.db.get_active_fingerprint(relpath)
                file_type = self.db.get_active_file_type(relpath)
                status = MODIFIED
                yield (relpath, path_hash, fingerprint, file_type, status)

    def walk(self, relpath=''):
        """Walk the checkpoint directory, starting from the specified path.
        
        Yields tuples of (relpath, abspath, fingerprint, file_type, status)
        
        NOTE: If relpath is a file (and not a directory), it will still 
        be yielded as normal.  This is different than python's os.walk,
        which for some reason doesn't yield a file in this case.
        
        """
        ignored_patterns = self.get_ignored_patterns()
        starting_path = self.get_abspath(relpath)
        
        if os.path.isfile(starting_path) or os.path.islink(starting_path):
            fingerprint = self.get_fingerprint(relpath)
            status = self.get_modification_status(relpath)
            file_type = self.filestore.get_file_type(starting_path)
            yield (relpath, starting_path, fingerprint, file_type, status)
        else:
            for root, dirs, files in os.walk(starting_path):
                # Ignore certain files and directories.  Note that 
                # dirs is modified inplace so that os.walk will not recurse
                # into those directories.
                files = filter_all_patterns(files, ignored_patterns)                
                for d in dirs:
                    if matches_any_pattern(d, ignored_patterns):
                        dirs.remove(d)
                # Iterate through files and directories looking for changes
                for x in dirs + files:
                    abspath = os.path.join(root, x)
                    relpath = self.get_relpath(abspath)
                    try:
                        fingerprint = self.get_fingerprint(relpath)
                        status = self.get_modification_status(relpath)
                        file_type = self.filestore.get_file_type(abspath)
                    except UnsupportedFileType, e:
                        log.warning(e.message)
                    else:
                        yield (
                            relpath, abspath, fingerprint, file_type, status
                        )

    @require_repository
    @lock
    def commit(self, paths=None):
        """Commit any unsaved changes to a new changeset.

        Optionally, a list of relative paths may be specified, and then only
        changes to those paths will be committed. For each directory specified
        in this list of paths, that directory will be walked recursively to
        find changes to commit.

        Returns the new changeset id.
        
        """
        # Wrap the actual __commit() call inside a transaction that will 
        # automatically rollback if an exception is thrown,
        # and automatically commit otherwise.
        try: 
            with self.db:
                return self.__commit(paths=paths)
        except NoChanges:
            log.info("No changes to commit")

    def __commit(self, paths=None):
        """See commit() for details."""
        log.info("Committing changes for directory %r" % self.directory)

        # Start a new changeset
        new_changeset = self.db.insert('changeset', dict(id=None)).lastrowid
        
        # Iterate through uncommited changes and commit them to the repository
        change_count = 0
        for change in self.__iterate_changes(paths=paths):
            change_count += 1
            # Unpack tuple of information about this change
            relpath, path_hash, fingerprint, file_type, status = change
            abspath = self.get_abspath(relpath)
            # Log what's happening
            log.info("%s\t%s" % (STATUS_CODES[status], relpath))
            # Commit any property changes
            self.db.commit_property_changes(relpath, new_changeset)
            # Commit file changes as appropriate for the type of change
            if status == ADDED:
                self.db.record_added(
                    new_changeset, relpath, path_hash,
                    fingerprint, file_type, status
                )
                self.filestore.save(abspath, path_hash, fingerprint, file_type)
            elif status == DELETED:
                self.db.record_deleted(
                    new_changeset, relpath, path_hash,
                    fingerprint, file_type, status
                )
            elif status == MODIFIED:
                self.db.record_modified(
                    new_changeset, relpath, path_hash, 
                    fingerprint, file_type, status
                )
                self.filestore.save(abspath, path_hash, fingerprint, file_type)
            else:
                raise CheckpointBug("Invalid modification status: %r" % status)

        # If there were no changes, roll back transaction
        if change_count == 0:
            raise NoChanges()
        else:
            log.info("New changeset: %s" % new_changeset)
            return new_changeset

    def __restore_active_set(self):
        """Undo all changes since the last commit.
        
        Returns the number of changes that were undone.
        
        """
        additions = []
        deletions = []
        modifications = []
        change_count = 0

        # Determine how to reverse all *uncommitted* changes
        for change in self.__iterate_changes():
            # Unpack tuple of information about this change
            relpath, path_hash, fingerprint, file_type, status = change
            abspath = self.get_abspath(relpath)
            # Peform the reverse of the change, to undo the change.
            action = None
            if status == ADDED:
                # Remove path
                action = DELETED
                deletions.append(abspath)
            elif status == DELETED:
                # Put path back where it was
                action = ADDED
                original_hash = self.db.get_active_hash(relpath)
                original_fingerprint = self.db.get_active_fingerprint(relpath)
                original_type = self.db.get_active_file_type(relpath)
                additions.append([
                    abspath, original_hash, original_fingerprint, 
                    original_type
                ])
            elif status == MODIFIED:
                # Locate and restore original path
                action = MODIFIED
                original_hash = self.db.get_active_hash(relpath)
                original_fingerprint = self.db.get_active_fingerprint(relpath)
                original_type = self.db.get_active_file_type(relpath)
                # Property changes alone will also show up as a MODIFICATION,
                # so ignore paths where there really wasn't a change.
                if not ((original_hash == path_hash) and
                       (original_fingerprint == fingerprint) and
                       (original_type == file_type)):
                    modifications.append([
                        abspath, original_hash, original_fingerprint, 
                        original_type
                    ])
            else:
                raise CheckpointBug("Invalid modification status: %r" % status)
            # Delete any uncommitted property changes
            self.db.delete('property', dict(changeset_id=None))
            # Log what's happening
            change_count += 1
            log.info("%s\t%s" % (STATUS_CODES[action], relpath))

        # Perform all file changes
        self.filestore.restore_multiple(modifications)
        self.filestore.restore_multiple(additions)
        self.filestore.delete_multiple(deletions)
        
        return change_count
    
    @require_repository
    @lock
    def revert(self, changeset=None):
        """Revert to a previous changeset.
        
        All uncommitted changes are reverted.  Then, if a changeset
        was specified, recent changesets are iterated in descending order
        and reverted, until the desired_changeset is reached.
        
        Returns the new changeset id.
        
        """
        # Wrap the actual __revert() call inside a transaction that will 
        # automatically rollback if an exception is thrown,
        # and automatically commit otherwise.
        try: 
            with self.db:
                return self.__revert(desired_changeset=changeset)
        except NoChanges:
            log.info("No changes to revert")
     
    def __revert(self, desired_changeset=None):
        """See revert() for details."""

        # Undo any uncommited changes.
        change_count = self.__restore_active_set()
        
        # If no changeset was specified, our work here is done.
        if desired_changeset is None: 
            if change_count == 0:
                raise NoChanges()
            else:
                return

        # Log what's happening.
        log.info("Reverting directory %r to changeset %s" % 
            (self.directory, desired_changeset)
        )
        
        # Make sure desired changeset is a valid changeset.
        if not self.db.exists('changeset', dict(id=desired_changeset)):
            raise RepositoryError("Invalid changeset: %s" % desired_changeset)

        # Start a new changeset to hold all the changes.
        new_changeset = self.db.insert('changeset', dict(id=None)).lastrowid

        # Iterate changesets in decending order (starting with the 
        # most recent) and reverse the changes made in each changeset,
        # until the desired_changeset is reached.
        change_count = 0
        for i in range(new_changeset-1, desired_changeset, -1):
            change_count += self.__revert_property_changes(i, new_changeset)
            change_count += self.__revert_file_changes(i, new_changeset)

        # Raise an error if there were no changes.  This allows the
        # actual revert() method to rollback the transaction and cancel
        # the unnecessary new changeset.
        if change_count == 0:
            raise NoChanges()
        else:
            log.info("New changeset: %s" % new_changeset)
            return new_changeset

    def __revert_property_changes(self, revert_changeset, new_changeset):
        """work-horse for __revert()"""
        # Iterate through property changes in revert_changeset
        property_changes = self.db.select('property',
            columns=['path', 'propname', 'propval', 'status'],
            where_clauses=dict(changeset_id=revert_changeset)
        )
        change_count = 0
        for change in property_changes:
            # Unpack data in the 'change' tuple
            (relpath, propname, propval, status) = change
            # Perform the reverse of the original modification
            action = None
            if status == ADDED:
                # Remove property
                self.db._change_property(
                    propname, propval, relpath, new_changeset, DELETED
                )
                # Log what's happening
                change_count += 1
                log.info("Property %r deleted from %r" % (propname, relpath))
            elif status == DELETED:
                # Restore property
                original_propval = self.db.get_property(
                    propname, relpath, max_changeset=revert_changeset-1
                )
                self.db._change_property(
                    propname, propval, relpath, new_changeset, ADDED
                )
                # Log what's happening
                change_count += 1
                log.info("Property %r set on %r" % (propname, relpath))
            elif status == MODIFIED:
                # Restore property
                original_propval = self.db.get_property(
                    propname, relpath, max_changeset=revert_changeset-1
                )
                self.db._change_property(
                    propname, propval, relpath, new_changeset, MODIFIED
                )
                # Log what's happening
                change_count += 1
                log.info("Property %r set on %r" % (propname, relpath))
            else:
                raise CheckpointBug(
                    "Invalid modification status: %r" % status
                )
        # Return a count of the changes that were undone
        return change_count

    def __revert_file_changes(self, revert_changeset, new_changeset):
        """work-horse for __revert()"""
        additions = []
        deletions = []
        modifications = []
        change_count = 0
        # Iterate through path changes in revert_changeset
        path_changes = self.db.select('modification', 
            columns=['path', 'hash', 'fingerprint', 'type', 'status'],
            where_clauses=dict(changeset_id=revert_changeset)
        )
        for change in path_changes:
            # Unpack data in the 'change' tuple
            (relpath, path_hash, fingerprint, file_type, status) = change
            abspath = self.get_abspath(relpath)
            # Perform the reverse of the original modification
            action = None
            if status == ADDED:
                # Remove path
                action = DELETED
                deletions.append(
                    (new_changeset, relpath, path_hash, 
                    fingerprint, file_type, action)
                )
            elif status == DELETED:
                # Restore path
                action = ADDED
                additions.append(
                    (new_changeset, relpath, path_hash, 
                    fingerprint, file_type, action)
                )
            elif status == MODIFIED:
                # Restore path
                action = MODIFIED
                # Locate the previous version of path
                last_version = self.db.get_previous_version(
                    relpath, revert_changeset
                )
                (last_hash, last_fingerprint, 
                last_type, last_status) = last_version
                # A file can not possibly be DELETED and then MODIFIED.
                # If the previous state was not ADDED or MODIFIED,
                # something is horribly wrong and could be a bug
                if last_status not in [ADDED, MODIFIED]:
                    message = dedent("""
                        DEBUG INFO:
                        path: %r
                        path_hash: %r
                        path_fingerprint: %r
                        revert_changeset: %r
                    """ % (abspath, path_hash, fingerprint, revert_changeset))
                    raise CheckpointBug(message)
                modifications.append(
                    (new_changeset, relpath, last_hash, 
                    last_fingerprint, last_type, action)
                )
            else:
                raise CheckpointBug(
                    "Invalid modification status: %r" % status
                )

        # Remove duplicates 
        deletions = filter_duplicates(deletions)
        additions = filter_duplicates(additions)
        modifications = filter_duplicates(modifications)

        # Prune additions and deletions so that we don't try to
        # add and delete the same exact thing.
        redundant_additions = []
        redundant_deletions = []
        for d in deletions:
            file_infos = d[:-1]
            corresponding_addition = file_infos + tuple([ADDED])
            if corresponding_addition in additions:
                additions.remove(corresponding_addition)
                redundant_deletions.append(d)
        for r in redundant_deletions:
            deletions.remove(r)

        # Perform all modifications, then additions, then deletions,
        # in that order.  This prevents most dependency problems.
        for changes in [modifications, additions]:
            path_changes = []
            for c in changes:
                (new_changeset, relpath, path_hash, 
                fingerprint, file_type, action) = c
                self.db.record_modified(*c)
                abspath = self.get_abspath(relpath)
                path_changes.append(
                    [abspath, path_hash, fingerprint, file_type]
                )
                # Log what's happening
                change_count += 1
                log.info("%s\t%s" % (STATUS_CODES[action], relpath))
            self.filestore.restore_multiple(path_changes)
        path_deletions = []
        for d in deletions:
            (new_changeset, relpath, path_hash, 
            fingerprint, file_type, action) = d
            self.db.record_deleted(*d)
            path_deletions.append(self.get_abspath(relpath))
            # Log what's happening
            change_count += 1
            log.info("%s\t%s" % (STATUS_CODES[action], relpath))
        self.filestore.delete_multiple(path_deletions)
        
        # Return a count of the file changes that were undone
        return change_count

    @require_repository
    def recover(self):
        """Attempt to repair directory and restore any missing files."""
        recovery_directory = self.__create_recovery_directory()
        try:
            self.__recover(recovery_directory)
        except:
            log.info(dedent("""
                --------------------------------------------------------------
                !!! Recovery Failed! !!!

                Checkpoint failed to restore directory %r.
            
                Further error messages may indicate the source of the failure.
            
                If files are missing, you may find them in the crash
                recovery directory %r
            
                Manual crash-recovery may be the only option.  
                Check the documentation for more information.
                --------------------------------------------------------------
                
            """ % (self.directory, recovery_directory)
            ))
            raise

    def __create_recovery_directory(self):
        """Create a new crash-recovery directory and return the path."""
        recovery_basedir = os.path.join(self.repository_path, 'recovery')
        if not os.path.exists(recovery_basedir):
            new_dir_num = 1
        else:
            new_dir_num = len(os.listdir(recovery_basedir)) + 1
        recovery_directory = os.path.join(recovery_basedir, str(new_dir_num))
        try:
            os.makedirs(recovery_directory)
        except (OSError, IOError), e:
            raise FileError(
                "Could not create a new crash-recovery directory %r: %s" %
                (recovery_directory, e)
            )
        return recovery_directory

    def __recover(self, recovery_directory):
        """See recover() for details"""
        log.info("Attempting to recover directory %r" % self.directory)
        # Move all existing files out of the checkpoint directory and
        # into a crash-recovery directory inside the repository
        for path in os.listdir(self.directory):
            # Skip the repository directory
            if path == self.get_basename():
                continue
            source = os.path.join(self.directory, path)
            destination = os.path.join(recovery_directory, path)
            try:
                shutil.move(source, destination)
            except (OSError, IOError), e:
                raise FileError(
                    "Could not move %r to recovery directory %r: %s" % 
                    (source, recovery_directory, e)
                )
        # Attempt to restore the active set of files
        self.__restore_active_set()
        # Delete any lockfiles
        if os.path.exists(self.lockfile_path):
            try:
                os.remove(self.lockfile_path)
            except (OSError, IOError), e:
                raise FileError(
                    "Could not remove lockfile %r:  %s" % 
                    (self.lockfile_path, e)
                )