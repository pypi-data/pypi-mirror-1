"""Checkpoint Repository management"""
from __future__ import with_statement

import os
import shutil
import pickle
import logging
from textwrap import dedent

from checkpoint.database import Database
from checkpoint.filestore import FileStore, FILE, DIRECTORY, LINK
from checkpoint.error import *
from checkpoint.util import *

__all_ = ['Repository']

log = logging.getLogger("checkpoint")

DEFAULT_REPOSITORY_BASENAME = '.cpt'

NO_CHANGE = 0
ADDED = 1
DELETED = 2
MODIFIED = 3

STATUS_CODES = {
    NO_CHANGE: '',
    ADDED: 'A',
    DELETED: 'D',
    MODIFIED: 'M'
}

class Repository(object):
    """Checkpoint Repository"""
    
    def __init__(self, directory):
        super(Repository, self).__init__()
        
        # Raise error if directory has not been created
        if not os.path.isdir(directory):
            raise NotFound("Could not find directory %r" % directory)
        
        self.directory = os.path.abspath(directory)
        self.path = self.__class__.get_path(self.directory)
        self.filestore = FileStore(self.path)
        self.db = Database(self.path)
        self.lockfile = os.path.join(self.path, 'lock')

    def lock(func):
        """Decorator that uses 'lockfiles' to allow for crash-recovery"""
        def wrapper(self, *args, **kwargs):
            # If lockfile exists, raise error and proceed no further
            if os.path.exists(self.lockfile):
                raise RepositoryLocked()
            # Otherwise, create lockfile and call function
            try:
                with open(self.lockfile, 'w') as f:
                    # Store the method and kwargs for the current operation
                    f.write("%s\n" % func.__name__)
                    pickle.dump(args, f)
                    pickle.dump(kwargs, f)
                    # Make ABSOLUTELY sure the lockfile is written to disk
                    f.flush()
                    os.fsync(f.fileno())
            except (OSError, IOError, pickle.PicklingError), e:
                raise FileError(
                    "Corrupt lockfile %r: %s" % (self.lockfile, e)
                )
            return_value = func(self, *args, **kwargs)
            # If function did not raise an error, remove lockfile
            try:
                os.remove(self.lockfile)
            except (OSError, IOError), e:
                raise FileError(
                    "Could not remove lockfile %r: %s" %
                    (self.lockfile, e)
                )
        return wrapper

    def is_locked(self):
        """Test if repository is locked."""
        if os.path.exists(self.lockfile):
            return True
        else:
            return False

    @classmethod
    def get_basename(cls):
        """Return the basename for the repository."""
        basename = DEFAULT_REPOSITORY_BASENAME
        try:
            basename = os.environ['CHECKPOINT_REPOSITORY_BASENAME']
        except KeyError:
            pass 
        return basename       

    @classmethod
    def get_path(cls, directory):
        """Return the repository path for a given directory."""
        # Determine repository path
        basename = cls.get_basename()
        directory = os.path.abspath(directory)
        return os.path.join(directory, basename)

    def get_ignored_patterns(self):
        """Determine the basename patterns (ex: '*.jpg') to ignore."""
        # Always ignore repositories
        ignored_patterns = [self.__class__.get_basename()]
        # Check for additional patterns specified by environment variables
        try:
            ignored_patterns.extend(
                os.environ['CHECKPOINT_IGNORED_PATTERNS'].split(':')
            )
        except KeyError:
            pass
        return ignored_patterns
    ignored_patterns = property(get_ignored_patterns)

    def initialize(self):
        """Initialize the repository."""
        log.info("Initializing repository for directory: %r" % self.directory)

        # Create repository directory and crash-recovery directory
        try:
            os.makedirs(self.path)
        except (OSError, IOError), e:
            raise FileError("Could not create repository %r: %s" % 
                (self.path, e)
            )

        # Initialize db and filestore
        self.db.initialize()
        self.filestore.initialize()
        
    def is_initialized(self):
        """Quickly test whether a repository has been initialized."""
        # Test if repository directory exists
        if os.path.isdir(self.path) and not os.path.islink(self.path):
            return True
        else:
            return False

    def get_current_changeset(self):
        """Return the last committed changeset id."""
        return self.db.current_changeset
    current_changeset = property(get_current_changeset)

    def delete_repository(self):
        """Completely delete the repository."""
        log.info("Deleting repository for directory %r" % self.directory)
        # Raise error if there is no repository to delete
        if not self.is_initialized():
            raise RepositoryError("Could not find repository %r" % self.path)
        # Delete repository, leaving the 'watched' directory untouched
        try:
            shutil.rmtree(self.path)
        except (OSError, IOError), e:
            raise FileError("Error deleting repository %r: %s" % 
                (self.path, e)
            )

    def modification_status(self, path, path_hash):
        """Return the modification status of the given file or directory.

        For files and directories that exist currently in the 'watch'ed
        directory, determine if file or directory was newly ADDED or 
        newly MODIFIED, and return the corresponding constant.  For files and 
        directories that do not currently exist on the file system, look in 
        the database to determine if the file or directory was recently 
        DELETED.  If the file or directory has not changed since the last 
        commit, then NO_CHANGE is returned.

        """
        # Determine file type, catching NotFound error for nonexistant files
        # but letting UnsupportedFileType errors through.
        try:
            file_type = self.filestore.get_file_type(path)
        except NotFound:
            pass
        exists_in_filesystem = os.path.lexists(path)
        exists_in_db = self.db.exists('active_set', dict(path=path))

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
            original_hash = self.db.get_active_hash(path)
            if unicode(original_hash) == unicode(path_hash):
                return NO_CHANGE
            else:
                return MODIFIED

    def changes(self):
        """Yield the set of repository changes since the last commit.

        Results are not sorted in any way, and the order of yield-ed
        results should not be relied on for any particular purpose.

        Special files (pipes, sockets, etc) are ignored.

        Paths that were renamed or moved will be detected as one path being 
        deleted and another path being added.
        
        """
        # Iterate through the 'active_set' database table (which stores the 
        # state of all files at the time of the last commit), and see if any 
        # of those files or directories have been DELETED
        active_set = self.db.select('active_set', 
            columns=['path', 'hash', 'type']
        )
        for path, path_hash, file_type in active_set:
            try:
                status = self.modification_status(path, path_hash)
            except UnsupportedFileType, e:
                log.warning(e.message)
            else:
                if status == DELETED:
                    yield (path, path_hash, file_type, status)
        
        # Walk directory and yield files and directories that 
        # were ADDED or MODIFIED since the last commit
        ignored_patterns = self.ignored_patterns
        for root, dirs, files in os.walk(self.directory):
            # Ignore certain files and directories.  Note that 
            # dirs is modified inplace so that os.walk will not recurse
            # into those directories.
            files = filter_all_patterns(files, ignored_patterns)                
            for d in dirs:
                if matches_any_pattern(d, ignored_patterns):
                    dirs.remove(d)
            # Iterate through files and directories looking for changes
            for x in dirs + files:
                path = os.path.join(root, x)
                try:
                    path_hash = sha1_hash(path)
                except (OSError, IOError), e:
                    raise FileError(
                        "Could not determine status of file %r: %s" %
                        (path, e)
                    )
                try:
                    status = self.modification_status(path, path_hash)
                except UnsupportedFileType, e:
                    log.warning(e.message)
                else:
                    # Yield only files/dirs that have changed
                    if status != NO_CHANGE:
                        file_type = self.filestore.get_file_type(path)
                        yield (path, path_hash, file_type, status)

    @lock
    def commit(self):
        """Commit any unsaved changes to a new changeset.
        
        Returns the new changeset id.
        
        """
        # Wrap the actual _commit() call inside a transaction that will 
        # automatically rollback if an exception is thrown,
        # and automatically commit otherwise.
        try: 
            with self.db:
                return self._commit()
        except NoChanges:
            log.info("No changes to commit")

    def _commit(self):
        """Workhorse for commit() method"""
        log.info("Committing changes for directory %r" % self.directory)

        # Start a new changeset
        new_changeset = self.db.insert('changeset', dict(id=None)).lastrowid
        
        # Iterate through changes and commit them to the repository
        changecount = 0
        for change in self.changes():
            path, path_hash, file_type, status = change
            # Log what's happening
            changecount += 1
            log.info("%s\t%s" % (STATUS_CODES[status], path))
            # Commit changes as appropriate for the type of change
            if status == ADDED:
                self.db.record_added(new_changeset, *change)
                self.filestore.save(path, path_hash, file_type)
            elif status == DELETED:
                self.db.record_deleted(new_changeset, *change)
            elif status == MODIFIED:
                self.db.record_modified(new_changeset, *change)
                self.filestore.save(path, path_hash, file_type)

        # If there were no changes, roll back transaction
        if changecount == 0:
            raise NoChanges()
        else:
            log.info("New changeset: %s" % new_changeset)
            return new_changeset

    def restore_active_set(self):
        """Undo all changes since the last commit.
        
        Returns the number of changes that were undone.
        
        """
        # Create queues so that changes can be applied in the correct order.  
        # For example, directory '/a/b' must be created before 
        # file '/a/b/c.txt' can be added.
        additions = []
        deletions = []
        modifications = []
        changecount = 0

        # Determine how to reverse all *uncommitted* changes
        for path, path_hash, file_type, status in self.changes():
            # Perform the reverse of the original modification
            action = None
            if status == ADDED:
                # Remove path
                action = DELETED
                deletions.append(path)
            elif status == DELETED:
                # Put path back where it was
                action = ADDED
                original_file_type = self.db.get_active_file_type(path)
                additions.append([path, path_hash, file_type])
            elif status == MODIFIED:
                # Locate and restore original path
                action = MODIFIED
                original_hash = self.db.get_active_hash(path)
                original_type = self.db.get_active_file_type(path)
                modifications.append([path, original_hash, original_type])
            # Log what's happening
            changecount += 1
            log.info("%s\t%s" % (STATUS_CODES[action], path))

        # Perform all modifications, then additions, then deletions, in that
        # order.  This prevents most dependency problems.
        self.filestore.restore_multiple(modifications)
        self.filestore.restore_multiple(additions)
        self.filestore.delete_multiple(deletions)
        
        return changecount
    
    @lock
    def revert(self, desired_changeset=None):
        """Revert to a previous changeset.
        
        All uncommitted changes are reverted.  Then, if a changeset
        was specified, recent changesets are iterated in descending order
        and reverted, until the desired_changeset is reached.
        
        Returns the new changeset id.
        
        """
        # Wrap the actual _revert() call inside a transaction that will 
        # automatically rollback if an exception is thrown,
        # and automatically commit otherwise.
        try: 
            with self.db:
                return self._revert(desired_changeset)
        except NoChanges:
            log.info("No changes to revert")
     
    def _revert(self, desired_changeset=None):
        """Workhorse for revert() method"""

        # Undo any uncommited changes.
        changecount = self.restore_active_set()
        
        # If no changeset was specified, our work here is done.
        if desired_changeset is None: 
            if changecount == 0:
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

        # Create queues so that changes can be applied in the correct 
        # order.  For example, directory '/a/b' must be created before 
        # file '/a/b/c.txt' can be added.
        additions = []
        deletions = []
        modifications = []

        # Iterate changesets in decending order (starting with the 
        # most recent) and reverse the changes made in each changeset,
        # until the desired_changeset is reached.
        for i in range(new_changeset-1, desired_changeset, -1):
            changeset_changes = self.db.select('modification', 
                columns=['changeset_id', 'path', 'hash', 'type', 'status'],
                where_clauses=dict(changeset_id=i)
            )
            for change in changeset_changes:
                # Perform the reverse of the original modification
                mod_changeset, path, path_hash, file_type, status = change
                action = None
                if status == ADDED:
                    # Remove path
                    action = DELETED
                    self.db.record_deleted(
                        new_changeset, path, path_hash, file_type, action
                    )
                    deletions.append(path)
                elif status == DELETED:
                    action = ADDED
                    self.db.record_added(
                        new_changeset, path, path_hash, file_type, action
                    )
                    additions.append([path, path_hash, file_type])
                elif status == MODIFIED:
                    action = MODIFIED
                    # Locate the previous version of path
                    last_version = self.db.get_previous_version(
                        path, path_hash, mod_changeset
                    )
                    last_hash, last_type, last_status = last_version
                    # A file can not possibly be DELETED and then MODIFIED.
                    # If the previous state was not ADDED or MODIFIED,
                    # something is horribly wrong and could be a bug
                    if last_status not in [ADDED, MODIFIED]:
                        message = textwrap.dedent("""
                            DEBUG INFO:
                            path: %r
                            path_hash: %r
                            mod_changeset: %r
                        """ % (path, path_hash, mod_changeset))
                        raise CheckpointBug(message)
                    self.db.record_modified(
                        new_changeset, path, last_hash, last_type, action
                    )
                    modifications.append([path, last_hash, last_type])
                    
                # Log what's happening
                changecount += 1
                log.info("%s\t%s" % (STATUS_CODES[action], path))

            # Perform all modifications, then additions, then deletions,
            # in that order.  This prevents most dependency problems.
            self.filestore.restore_multiple(modifications)
            self.filestore.restore_multiple(additions)
            self.filestore.delete_multiple(deletions)
        
        # Raise an error if there were no changes.  This allows the
        # actual revert() method to rollback the transaction and cancel
        # the unnecessary new changeset.
        if changecount == 0:
            raise NoChanges()
        else:
            log.info("New changeset: %s" % new_changeset)
            return new_changeset

    def get_recovery_directory(self):
        """Create a new crash-recovery directory and return the path."""
        recovery_basedir = os.path.join(self.path, 'recovery')
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

    def recover(self):
        """Attempt to repair directory and restore any missing files."""
        recovery_directory = self.get_recovery_directory()
        try:
            self._recover(recovery_directory)
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

    def _recover(self, recovery_directory):
        """Workhorse for the recover() method"""
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
        self.restore_active_set()
        # Delete any lockfiles
        if os.path.exists(self.lockfile):
            try:
                os.remove(self.lockfile)
            except (OSError, IOError), e:
                raise FileError(
                    "Could not remove lockfile %r:  %s" % (self.lockfile, e)
                )