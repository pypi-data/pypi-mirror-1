"""
Docstrings rule!
"""

import os
import sys
import errno
import shutil
import logging
import hashlib
import textwrap
import sqlite3
import operator
from traceback import format_stack

from release import NAME, VERSION, DESCRIPTION

# USER NOTES: 
# * python 2.5 or greater is required
# * Linked directories and special files (pipes, sockets, etc) are ignored
# * Files that were renamed will be detected as one file being
#   deleted and another file being added.  Due to concurrency problems there
#   is no way around this.  "svn mv" does the same thing, try it!
# * Concurrency is NOT supported.  If you have two copies of Checkpoint
#   running on the same directory, and one is trying to do a commit and the
#   other is trying to do a revert, crazy shit will happen.

# IMPLEMENTATION NOTES:
# * When Checkpoint "reverts" to a previous changeset, a new changeset is
#   is created and changes are applied to that changeset until it is 
#   equivalent to the desired changeset.  This is a deliberate design 
#   decision, and while it wastes some space in the database, it doesn't
#   create unnecessary duplicates of backup files, and more importantly
#   it keeps the implementation simple and easy to understand.
# * Checkpoint is optimized so that it's quicker to undo recent changesets
#   than it is to go further back.  This is a deliberate design decision
#   that makes Checkpoint very friendly with typical usage where the user
#   quickly realizes a mistake has been made in some file and wishes to
#   "undo" that recent change.
# * Directories can only be ADDED or DELETED.  They cannot be MODIFIED.
#   This is to say that if a file is MODIFIED, that does not change the
#   status of the directory it is in.  Similarly, if a directory with 
#   (say) two files in it is renamed, that will show up as two files 
#   and one directory that were DELETED, and then two files and one 
#   directory that were ADDED.  However, because the SHA1 hash is used
#   to store the backup files, this operation will *not* result in any
#   additional (and unnecessary) disk space being used.
# * Python 2.5 is required for decorators, context managers, sqlite3, hashlib

SUCCESS = 0
ERROR = 1

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

REPOSITORY_BASENAME = '.cpt'

log = logging.getLogger("checkpoint")

def sha1_hash(file_path):
    """Return sha1 hash of specified file"""
    hash_buffer_size = 1024
    f = open(file_path, 'rb')
    h = hashlib.sha1()

    while True:
        data = f.read(hash_buffer_size)
        if data:
            h.update(data)
        else:
            break

    f.close()    
    return h.hexdigest()

class CheckpointBug(Exception):
    """Error indicates a bug in the checkpoint API"""
    def __init__(self, message=""):
        super(CheckpointBug, self).__init__()
        self.message = (
            "Unrecoverable Error!\n" + message + "\n" +
            ("Traceback (most recent call last):\n%s" % format_stack()) +
            textwrap.dedent("""
                This could be a bug in Checkpoint.
                Please report this bug as described at
                http://something something something....
            """)
        )
class CheckpointError(Exception):
    """Base class for anticipated errors in the checkpoint package"""
class NotFound(CheckpointError):
    """Specified file or directory does not exist"""
class InvalidCommand(CheckpointError):
    """Not a valid Checkpoint command"""
class FileError(CheckpointError):
    """File operation error - error during rm, copy, mv, etc"""
class RepositoryError(CheckpointError):
    """Repository operation error - error during read, write, or create"""

    
class Checkpoint(object):
    """Checkpoint management class"""
    COMMANDS = ['watch', 'status', 'commit', 'revert', 'forget']

    def __init__(self, directory=None):
        super(Checkpoint, self).__init__()

        # Raise error if directory has not been created
        if not os.path.isdir(directory):
            raise NotFound("Could not open directory: %r" % directory)
            
        # Determine configuration values
        self.directory = os.path.abspath(directory)
        self.repository = self.__class__.repository_path(directory)
        self.filestore = self.__class__.filestore_path(self.repository)
        self.dbpath = self.__class__.db_path(self.repository)
        self._db = None
    
    def getdb(self):
        """Return active database connection, creating one if necessary"""
        try:
            if self._db is None:
                self._db = sqlite3.connect(self.dbpath)
                # self._db.row_factory = sqlite3.Row
        except sqlite3.OperationalError, e:
            message = "Could not open repository database: %s" % e.message
            raise RepositoryError(message)
        return self._db
            
    def setdb(self, value):
        """Set active database connection, overwriting the existing one"""
        self._db = value
    
    def deletedb(self):
        self._db.close()
        del self._db
    
    db = property(getdb, setdb, deletedb, """Repository database""")
    
    def dispatch(self, command, options):
        """Dispatch to specfied command (Useful for CLI programs)"""
        if command not in self.__class__.COMMANDS:
            raise InvalidCommand("Unknown command: '%s'" % command)
        else:
            method = getattr(self, command)
            if command == 'revert':
                method(options.changeset)
            else:
                method()

    @classmethod
    def filestore_path(cls, repository):
        """Return the filestore path for a given repository"""
        repository = os.path.abspath(repository)
        return os.path.join(repository, 'files')

    @classmethod
    def db_path(cls, repository):
        """Return the database file path for a given repository"""
        repository = os.path.abspath(repository)
        return os.path.join(repository, 'data.sqlite')
        
    @classmethod
    def repository_basename(cls):
        """Return the basename for the repository"""
        try: 
            return os.environ['CHECKPOINT_REPOSITORY_BASENAME']
        except KeyError:
            return REPOSITORY_BASENAME
            
    @classmethod
    def repository_path(cls, directory):
        """Return the repository path for a given directory"""
        directory = os.path.abspath(directory)
        return os.path.join(directory, cls.repository_basename())

    @classmethod
    def has_valid_repository(cls, directory):
        """Thoroughly test the integrity of a directory's repository"""
        pass

    @classmethod
    def has_repository(cls, directory):
        """Quickly test whether a directory has a repository"""
        # Determine path information
        directory = os.path.abspath(directory)
        repository = cls.repository_path(directory)
        # Test if repository directory exists
        if os.path.isdir(repository) and not os.path.islink(repository):
            return True
        else:
            return False
    
    def forget(self):
        """Permanently delete repository"""
        # Raise error if there is no repository to delete
        if not self.__class__.has_repository(self.directory):
            raise RepositoryError(
                "Could not find repository: %r" %
                self.__class__.repository_path(self.directory)
            )
            
        # Delete repository directory and everything in it
        log.info("Forgetting directory: %r" % self.directory)
        try:
            shutil.rmtree(self.repository)
        except OSError, e:
            raise FileError("Error removing repository (%s): %s" % 
                (self.repository, str(e))
            )

    def watch(self):
        """Initialize repository"""        
        log.info("Watching directory: %r" % self.directory)
        
        # Raise an error if repository already exists
        if (self.__class__.has_repository(self.directory)):
            raise RepositoryError(
                "Repository (%s) already exists" % self.repository
            )
        
        # Create necessary directories
        try:
            os.makedirs(self.repository)
            os.makedirs(self.filestore)
        except OSError, e:
            raise FileError("Could not create repository (%s): %s" % 
                (self.repository, str(e))
            )
        
        # Create database tables
        self.db.executescript("""
            CREATE TABLE changeset (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE modification (
                path TEXT NOT NULL, 
                hash TEXT DEFAULT NULL,
                status INTEGER NOT NULL,
                changeset_id INTEGER NOT NULL
                    CONSTRAINT fk_changeset_id
                        REFERENCES changeset(id) 
                        ON DELETE CASCADE
            );
            CREATE TABLE active_set (
                path TEXT NOT NULL PRIMARY KEY,
                hash TEXT DEFAULT NULL
            );
        """)
        # Emulate foreign keys (which aren't enforced by SQLite)
        # using a series of triggers
        self.db.executescript(""" 
            -- Foreign Key Preventing insert
            CREATE TRIGGER fki_modification_changeset_id_changeset_id
            BEFORE INSERT ON [modification]
            FOR EACH ROW BEGIN
              SELECT RAISE(ROLLBACK, 'invalid changeset id')
              WHERE (SELECT id FROM changeset WHERE id = NEW.changeset_id) 
              IS NULL;
            END;
            -- Foreign key preventing update
            CREATE TRIGGER fku_modification_changeset_id_changeset_id
            BEFORE UPDATE ON [modification]
            FOR EACH ROW BEGIN
              SELECT RAISE(ROLLBACK, 'invalid changeset id')
              WHERE (SELECT id FROM changeset WHERE id = NEW.changeset_id)
              IS NULL;
            END;
            -- Cascading Delete
            CREATE TRIGGER fkdc_modification_changeset_id_changeset_id
            BEFORE DELETE ON changeset
            FOR EACH ROW BEGIN
              DELETE FROM modification 
              WHERE modification.changeset_id = OLD.id;
            END;
        """)

        # Make sure there is no pending transaction
        self.db.commit()

        # Commit everything in the Checkpoint directory to the repository
        self.commit()
        
    def status(self):
        """Print a list of changes since last commit"""
        log.info("Printing status of directory: %r" % self.directory)
        
        # Determine the current changeset
        sql = "SELECT MAX(id) FROM changeset"
        [changeset] = self.db.execute(sql).fetchone()
        
        # Print changes to stdout
        print "Changes since changeset %s..." % changeset
        for (path, status, file_hash) in self.changes():
            print "%s\t%s" % (STATUS_CODES[status], path)
    
    def modification_status(self, path, file_hash):
        """Return the modification status of the given file or directory
        
        For files and directories that exist currently in the 'watch'ed
        directory, determine if file or directory was newly ADDED or 
        newly MODIFIED, and return the corresponding constant.  For files and 
        directories that do not currently exist on the file system, look in 
        the database to determine if the file or directory was recently 
        DELETED.  If the file or directory has not changed since the last 
        commit, then NO_CHANGE is returned.
        
        Raises a TypeError if path is a link, pipe, socket, device, or 
        anything besides a regular file or directory.  Only regular files
        and directories are accepted.
        
        """
        # Test if the path is a regular file or a directory.
        # Both variables will be false if the path is a link, pipe, socket,
        # device, or if it doesn't exist on the filesystem.
        path_is_file = os.path.isfile(path)
        path_is_directory = os.path.isdir(path) and not os.path.islink(path)
        
        # Get a cursor to the database
        cursor = self.db.cursor()
        
        # If the path exists in the database but it's not showing up as a
        # regular file or directory on the filesystem, assume it was DELETED.
        sql = "SELECT * FROM active_set WHERE path = ? LIMIT 1"
        results = cursor.execute(sql, [path]).fetchone()
        if results is not None and not (path_is_file or path_is_directory):
            return DELETED
        
        # Raise error if file type is unsupported
        if not (path_is_file or path_is_directory):
            raise TypeError("Unsupported file type: %r" % path)
        
        # If path is a directory that exists on the filesystem but 
        # not in the db, assume it was ADDED
        if path_is_directory:
            sql = "SELECT * FROM active_set WHERE path = ? LIMIT 1"
            results = cursor.execute(sql, [path]).fetchone()
            if results is None:
                return ADDED
            else: 
                return NO_CHANGE

        # If path is a regular file that exists on the filesystem...
        if path_is_file:
            # Look for file path in db
            sql = "SELECT hash FROM active_set WHERE path = ? LIMIT 1"
            results = cursor.execute(sql, [path]).fetchone()
            # If path is in db and hash matches, assume there was NO_CHANGE
            # If path is in db but hash is different, assume it was MODIFIED
            if results is not None:
                original_file_hash = results[0]
                if unicode(original_file_hash) == unicode(file_hash):
                    return NO_CHANGE
                else:
                    return MODIFIED
            # If the file path is not in the db, assume the file was added
            return ADDED

        # If no tests have passed, something is very wrong, and the problem
        # should be reported to checkpoint developers
        message = textwrap.dedent("""
            DEBUG INFO:
            path: %r
            file_hash: %r
        """ % (path, file_hash))
        raise CheckpointBug(message)
    
    def changes(self):
        """Yield the set of repository changes since the last commit.
        
        Results are not sorted in any way, and the order of yield-ed
        results should not be relied on for any particular purpose.
        
        Links and special files (pipes, sockets, etc) are ignored.  Only
        regular files and regular directories will be inspected.
        
        Files that were renamed will be detected as one 
        file being deleted and another file being added.
        """
        # Determine path basenames to ignore
        ignored_paths = []
        try:
            ignored_paths.extend(
                os.environ['CHECKPOINT_IGNORED_PATHS'].split(':')
            )
        except KeyError:
            pass

        # Always Ignore repositories
        ignored_paths.append(self.__class__.repository_basename())
        
        # Walk directory and yield files and directories that 
        # were ADDED or MODIFIED since the last commit
        for root, dirs, files in os.walk(self.directory):
            # Ignore certain files and directories.  Note that 
            # dirs is modified inplace so that os.walk will not recurse
            # into those directories.
            files = [f for f in files if f not in ignored_paths]
            for d in dirs:
                if d in ignored_paths:
                    dirs.remove(d)
            # Iterate through files and directories looking for changes
            for x in dirs + files:
                path = os.path.join(root, x)     
                # Ignore links
                if os.path.islink(path):
                    log.warning("Unsupported file type (link): %r" % path)
                    continue
                # Specify no hash for a directory
                elif os.path.isdir(path):
                    file_hash = None
                # Specify a SHA1 hash for a regular file
                elif os.path.isfile(path):
                    file_hash = sha1_hash(path)
                # Ignore special files (pipes, sockets, etc):
                else:
                    log.warning("Unsupported file type (special): %r" % path)
                    continue
                # Yield files/dirs that have changed
                status = self.modification_status(path, file_hash)
                if status != NO_CHANGE:
                    yield (path, status, file_hash)
                    
        # Iterate through the 'active_set' database table (which stores the 
        # state of all files at the time of the last commit), and see if any 
        # of those files or directories have been DELETED
        results = self.db.execute("SELECT path, hash FROM active_set")
        for (active_path, active_hash) in results:
            status = self.modification_status(active_path, active_hash)
            if status == DELETED:
                yield (active_path, status, active_hash)

    def __insert(self, table, columns, values):
        """Perform INSERT on table with the given values"""
        # INSERT INTO table(column_a, column_b, ...) VALUES(?, ?, ...)
        sql = "INSERT INTO %s(%s) values(%s)" % (
            table,
            ", ".join(columns),
            ", ".join(['?' for v in values])
        )
        log.debug("__insert sql: %s, %r" % (sql, values))
        return self.db.execute(sql, values)

    def __delete(self, table, where_columns, where_values):
        """Perform DELETE on table with the given constraints"""
        # "DELETE FROM table WHERE column_a = ? AND column_b = ? AND ..."
        # If a where_value is None, use the IS NULL sql syntax
        where_clauses = []
        parameters = []
        for (col, val) in zip(where_columns, where_values):
            if val is None:
                where_clauses.append("%s IS NULL" % col)
            else:
                where_clauses.append("%s = ?" % col)
                parameters.append(val)
        sql = "DELETE FROM %s" % table
        if len(where_clauses) > 0:
            sql += " WHERE %s" % " AND ".join(where_clauses)
        log.debug("__delete sql: %s, %r" % (sql, parameters))
        return self.db.execute(sql, parameters)

    def __store(self, file_path, file_hash):
        """Save the specified file to the filestore"""
        destination = os.path.join(self.filestore, file_hash)
        log.debug("__store: path: %r, hash: %r, destination: %r" % (
            file_path, file_hash, destination
        ))
        try:
            shutil.copy2(file_path, destination)
        except OSError, e:
            raise FileError(
                """Error storing file %r into repository file %r: %s""" %
                (file_path, destination, str(e))
            )
            
    def __retrieve(self, path, file_hash):
        """Restore the specified file or directory"""
        # If file_hash is None, path is a directory
        log.debug("__retrieve path: %r, hash: %r" % (path, file_hash))
        if file_hash is None:
            try:
                os.makedirs(path)
            except OSError, e:
                raise FileError(
                    """Error restoring directory %r: %s""" % (path, str(e))
                )
        # If file_hash is not None, path is a file
        else:        
            source = os.path.join(self.filestore, file_hash)
            try:
                shutil.copy2(source, path)
            except OSError, e:
                raise FileError(
                    """Error restoring file %r from repository file %r: %s""" %
                    (path, source, str(e))
                )
        
    def commit(self):
        """Commit changes"""
        log.info("Committing changes for directory: %s" % self.directory)
        
        # Begin a transaction with the database, which will be automatically
        # rolled back if the computer crashes or an exception is thrown
        c = self.db.cursor()
        
        # Start a new changeset
        c.execute("INSERT INTO changeset(id) VALUES(null)")
        new_changeset = c.lastrowid
        
        # Iterate through changes and commit them to the repository
        changecount = 0
        for (path, status, file_hash) in self.changes():
            # Log what's happening
            changecount += 1
            log.info("%s\t%s" % (STATUS_CODES[status], path))
            
            # Determine if path is file or directory, based on whether or
            # not a file_hash was supplied by self.changes()
            is_file = file_hash is not None
            
            # Commit changes as appropriate for the type of change
            if status == ADDED:
                # Add this record to the list of active files in the db
                self.__insert(
                    'active_set', ['path', 'hash'], [path, file_hash]
                )
                # If path is a file, save it to the filestore
                if is_file:
                    self.__store(path, file_hash)
            elif status == DELETED:
                # Remove this record from the list of active files in the db
                self.__delete(
                    'active_set', ['path', 'hash'], [path, file_hash]
                )
            elif status == MODIFIED:
                # Apply this change to the list of active files in the db
                self.__delete('active_set', ['path'], [path])
                self.__insert(
                    'active_set', ['path', 'hash'], [path, file_hash]
                )
                # Save the new version of the file into the filestore
                self.__store(path, file_hash)
            else:
                # If no tests have passed, something is very wrong, and the 
                # problem should be reported to checkpoint developers
                message = textwrap.dedent("""
                    DEBUG INFO:
                    path: %r
                    status: %r
                    file_hash: %r
                """ % (path, status, file_hash))
                raise CheckpointBug(message)

            # For all valid modifications, record the modification in the db
            self.__insert('modification',
                ['path', 'hash', 'status', 'changeset_id'],
                [path, file_hash, status, new_changeset]
            )

        # If there were no changes, roll back transaction
        if changecount == 0:
            self.db.rollback()
            log.info("No changes to commit")
        else:
            # Commit changes now that all files have been safely saved
            # WHOOOAAAA actually we want to do a fsync or something to make
            # sure they were REALLY REALLY saved.
            self.db.commit()        
            log.info("New changeset: %s" % new_changeset)

    def revert(self, desired_changeset=None):
        """Revert to a previous changeset"""
        # Log what's happening
        changecount = 0
        log.info("Reverting directory %r to changeset %s" % 
            (self.directory, desired_changeset)
        )                

        # Begin a transaction with the database, which will be automatically
        # rolled back if the computer crashes or an exception is thrown
        c = self.db.cursor()
        
        # If changeset was specified, make sure it is valid
        if desired_changeset is not None:
            sql = "SELECT * FROM changeset WHERE id = ? LIMIT 1"
            results = c.execute(sql, [desired_changeset]).fetchone()
            if results is None: 
                raise RepositoryError(
                    "Invalid changeset: %s" % desired_changeset
                )

        # Start a new changeset to hold all the changes
        c.execute("INSERT INTO changeset(id) VALUES(null)")
        new_changeset = c.lastrowid

        # Use a queue so that changes can be applied in the correct order.  
        # For example, directory '/a/b' must be created before 
        # file '/a/b/c.txt' can be added.
        additions = []
        deletions = []
        modifications = []

        # Undo all *uncommitted* changes
        for (path, status, file_hash) in self.changes():
            # Perform the reverse of the original modification
            changecount += 1
            action = None
            if status == ADDED:
                # Remove file
                action = DELETED
                deletions.append([path, file_hash])
            elif status == DELETED:
                # Put file back where it was
                action = ADDED
                additions.append([path, file_hash])
            elif status == MODIFIED:
                # Locate and restore original file
                action = MODIFIED
                sql = "SELECT hash FROM active_set WHERE path = ?"
                row = c.execute(sql, [path]).fetchone()
                if row is not None:
                    [original_hash] = row
                    modifications.append([path, original_hash])
            else:
                # If no tests have passed, something is very wrong, and the 
                # problem should be reported to checkpoint developers
                raise CheckpointError(textwrap.dedent("""
                    DEBUG INFO:
                    path: %r
                    status: %r
                    file_hash: %r
                """ % (path, status, file_hash)))
            # Log what's happening
            log.info("%s\t%s" % (STATUS_CODES[action], path))

        # Perform file modification operations in ANY order
        for (path, previous_hash) in modifications:
            self.__retrieve(path, previous_hash)
    
        # Perform file additions in order of ascending path length.
        # This is a clever way to add '/a/b/ before adding '/a/b/c'
        ascending_length = lambda x,y: len(x) - len(y) 
        additions.sort(cmp=ascending_length, key=operator.itemgetter(0))
        for (path, file_hash) in additions:
            self.__retrieve(path, file_hash)
    
        # Perform file deletions in order of descending length.
        # This is a clever way to delete '/a/b' before deleting '/a'
        deletions.sort(cmp=ascending_length, key=operator.itemgetter(0), reverse=True)
        for (path, file_hash) in deletions:
            try:
                if os.path.isdir(path) and not os.path.islink(path):
                    os.rmdir(path)
                elif os.path.isfile(path):
                    os.remove(path)
            except OSError, e:
                raise FileError("Error removing path (%s): %s" % 
                    (path, str(e))
                )




        # If a desired_changeset was specified, go through all changesets
        # in decending order (starting with the most recent) and reverse
        # the changes made in those changesets, until the desired_changeset
        # is reached.
        if desired_changeset is not None:
            for i in range(new_changeset-1, desired_changeset, -1):            
                sql = ("SELECT path, hash, status, changeset_id "
                       "FROM modification WHERE changeset_id = ?")
                results = c.execute(sql, [i])
                for (path, file_hash, status, modification_changeset) in results:
                    # Perform the reverse of the original modification
                    changecount += 1
                    action = None

                    if status == ADDED:
                        # Remove this record from the list of active files in the db
                        self.__delete(
                            'active_set', ['path', 'hash'], [path, file_hash]
                        )
                        # Queue the file deletion for later
                        action = DELETED
                        deletions.append([path, file_hash])
                    elif status == DELETED:
                        # Insert this record into the list of active files in the db
                        self.__insert(
                            'active_set', ['path', 'hash'], [path, file_hash]
                        )
                        # Queue the file addition for later
                        action = ADDED
                        additions.append([path, file_hash])
                    elif status == MODIFIED:
                        # Locate the previous version of the file just before
                        # it was modified.
                        c2 = self.db.cursor() # Need 2nd cursor for 2nd result set
                        sql2 = ("SELECT hash, status FROM modification"
                                "WHERE path = ? AND changeset_id < ? "
                                "ORDER BY changeset_id DESC LIMIT 1")
                        results2 = c2.execute(sql2, [path, modification_changeset])
                        row2 = results2.fetchone()
                        if row2 is not None:
                            (previous_hash, previous_status) = row2
                        # A file can not possibly be DELETED and then MODIFIED.
                        # If the previous state was not ADDED or MODIFIED,
                        # something is horribly wrong and could be a bug
                        if row2 is None or previous_status not in [ADDED, MODIFIED]:
                            message = textwrap.dedent("""
                                DEBUG INFO:
                                path: %r
                                status: %r
                                file_hash: %r
                                modification_changeset: %r
                            """ % (path, status, file_hash, modification_changeset))
                            raise CheckpointBug(message)

                        # Apply this change to the list of active files in the db
                        self.__delete('active_set', ['path'], [path])
                        self.__insert(
                            'active_set', ['path', 'hash'], [path, previous_hash]
                        )
                        # Queue the file operation
                        action = MODIFIED
                        modifications.append([path, previous_hash])
                    else:
                        # If no tests have passed, something is very wrong, and the 
                        # problem should be reported to checkpoint developers
                        raise CheckpointError(textwrap.dedent("""
                            DEBUG INFO:
                            path: %r
                            status: %r
                            file_hash: %r
                            changeset: %r
                        """ % (path, status, file_hash, modification_changeset)))
            
                    # Log what's happening
                    log.info("%s\t%s" % (STATUS_CODES[action], path))
                
                    # For all valid modifications, record the modification in the db
                    self.__insert('modification',
                        ['path', 'hash', 'status', 'changeset_id'],
                        [path, file_hash, action, new_changeset]
                    )

                # Perform file modification operations in ANY order
                for (path, previous_hash) in modifications:
                    self.__retrieve(path, previous_hash)
            
                # Perform file additions in order of ascending length.
                # This is a clever way to add '/a/b/ before adding '/a/b/c'
                ascending_length = lambda x,y: len(x) - len(y) 
                additions.sort(cmp=ascending_length, key=operator.itemgetter(0))
                for (path, file_hash) in additions:
                    self.__retrieve(path, file_hash)
            
                # Perform file deletions in order of descending length.
                # This is a clever way to delete '/a/b' before deleting '/a'
                deletions.sort(cmp=ascending_length, key=operator.itemgetter(0), reverse=True)
                for (path, file_hash) in deletions:
                    try:
                        if os.path.isdir(path) and not os.path.islink(path):
                            os.rmdir(path)
                        elif os.path.isfile(path):
                            os.remove(path)
                    except OSError, e:
                        raise FileError("Error removing path (%s): %s" % 
                            (path, str(e))
                        )

        # If there were no changes, roll back transaction
        if changecount == 0:
            self.db.rollback()
            log.info("No changes to revert")
        else:
            # Commit changes now that all files have been safely saved
            # WHOOOAAAA actually we want to do a fsync or something to make
            # sure they were REALLY REALLY saved.
            self.db.commit()        
            log.info("New changeset: %s" % new_changeset)

def main(argv=sys.argv):
    
    usage = """
        usage:  %(prog)s <subcommand> [options] [args]
        Checkpoint command-line client, version %(version)s

        Most subcommands accept a directory argument.  If this argument is not
        specified, the current directory will be used by default.

        Available subcommands:
            watch [<dir>]                   Watch directory for changes
            status [<dir>]                  List all changes since last commit
            commit [<dir>]                  Save all changes since last commit
            revert -c changeset [<dir>]     Revert to a previous changeset
            forget [<dir>]                  Delete saved history of changes
    
        %(description)s
        For additional information, see %(url)s
    """ % dict(
        prog=os.path.basename(argv[0]),
        description=DESCRIPTION,
        version=VERSION,
        url='http://url'
    )
    usage = textwrap.dedent(usage)

    # Configure logging.  Since this is a command-line-interface (CLI),
    # logging goes to stdout, and log level is set to INFO so user can see
    # what the CLI is doing.  Note: log is defined at the module level
    log_level = logging.INFO
    try:
        if int(os.environ['CHECKPOINT_DEBUG']) == 1:
            log_level = logging.DEBUG
    except KeyError:
        pass
    log.setLevel(log_level) 
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter('%(message)s'))
    log.addHandler(handler)


    # Determine Checkpoint command
    try:
        command = argv[1]
    except IndexError:
        print usage
        return ERROR
        
    # Determine command options
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option('-c', dest="changeset", default=None, type='int')
    try:
        (options, extra_args) = parser.parse_args(argv[2:])
    except:
        print usage
        return ERROR

    # Determine Checkpoint directory (default to current directory)
    if len(extra_args) > 0:
        directory = extra_args[0]
    else:
        directory = os.getcwd()

    # Dispatch to command handler
    try:
        manager = Checkpoint(directory)
        return manager.dispatch(command, options)
    except CheckpointError, e:
        print >> sys.stderr, "%s\n" % e.message
        return ERROR

if __name__ == '__main__':
    sys.exit(main())