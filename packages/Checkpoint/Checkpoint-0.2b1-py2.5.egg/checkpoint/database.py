"""Database abstraction layer"""

import os
import sqlite3
import logging

from checkpoint.constants import DELETED, RAISE_ERR, ADDED, DELETED, MODIFIED
from checkpoint.error import (
    RepositoryError, UninitializedRepositoryError, PropertyNotFound
)

__all__ = ['Database']

log = logging.getLogger("checkpoint")
#logging.basicConfig(level=logging.DEBUG)

class Database(object):
    """Context Manager and Wrapper class for all your database needs."""
    def __init__(self, repository_dir):
        self.db_path = self.get_path(repository_dir)
        self._db = None

    def __enter__(self):
        """Begin a transaction"""
        # sqlite module automatically opens transactions, nothing to do here.
        return self
        
    def __exit__(self, type, value, traceback):
        """Rollback transaction on exception, otherwise Commit transaction"""
        if type is None and value is None and traceback is None:
            # No exception, so commit transaction.
            self.db.commit()
        else:
            # Exception occurred, so rollback transaction.
            self.db.rollback()
        # Return False to allow exception to bubble up
        return False

    @staticmethod
    def get_path(repository_dir):
        """Return the database file path for a given repository"""
        return os.path.join(os.path.abspath(repository_dir), 'data.sqlite')

    def get_db(self):
        """Return active database connection, creating one if necessary"""
        try:
            if self._db is None:
                self._db = sqlite3.Connection(self.db_path)
                #self._db.row_factory = sqlite3.Row # for access by colname
        except sqlite3.OperationalError, e:
            if not self.is_initialized():
                raise UninitializedRepositoryError
            else:
                message = "Could not open repository database: %s" % e.message
                raise RepositoryError(message)
        return self._db
    db = property(get_db)
    
    def initialize(self):
        """Initialize database"""
        
        # Create tables
        self.db.executescript("""
            CREATE TABLE changeset (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX idx_changeset ON changeset(id, date);
            
            -- Store data on file modifications
            CREATE TABLE modification (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                path TEXT NOT NULL, 
                hash TEXT DEFAULT NULL,
                fingerprint TEXT DEFAULT NULL,
                type INTEGER NOT NULL,
                status INTEGER NOT NULL,
                changeset_id INTEGER
                    CONSTRAINT fk_changeset_id
                        REFERENCES changeset(id) 
                        ON DELETE CASCADE
            );
            CREATE INDEX idx_modification ON modification(id, changeset_id);
            
            -- Store data on property modifications
            CREATE TABLE property (
                path TEXT NOT NULL,
                changeset_id INTEGER,
                propname TEXT NOT NULL,
                propval TEXT NOT NULL,
                status INTEGER NOT NULL
            );
            CREATE INDEX idx_property ON property(
                path, changeset_id, propname, propval, status
            );
            
            CREATE TABLE active_set (
                path TEXT NOT NULL PRIMARY KEY,
                hash TEXT DEFAULT NULL,
                fingerprint TEXT DEFAULT NULL,
                type INTEGER NOT NULL  
            );
        """)
        
        # Emulate foreign keys (which aren't enforced by SQLite)
        # using a series of triggers
        for table in ['modification']:
            self.db.executescript(""" 
                -- Prevent insert with invalid foreign key
                CREATE TRIGGER fki_%(table)s_changeset_id
                BEFORE INSERT ON %(table)s
                FOR EACH ROW BEGIN
                  SELECT RAISE(ROLLBACK, 'invalid changeset id')
                  WHERE (SELECT id FROM changeset WHERE id = NEW.changeset_id) 
                  IS NULL;
                END;
                -- Prevent update with invalid foreign key
                CREATE TRIGGER fku_%(table)s_changeset_id
                BEFORE UPDATE ON %(table)s
                FOR EACH ROW BEGIN
                  SELECT RAISE(ROLLBACK, 'invalid changeset id')
                  WHERE (SELECT id FROM changeset WHERE id = NEW.changeset_id)
                  IS NULL;
                END;
                -- Cascading Delete
                CREATE TRIGGER fkdc_%(table)s_changeset_id
                BEFORE DELETE ON changeset
                FOR EACH ROW BEGIN
                  DELETE FROM %(table)s
                  WHERE %(table)s.changeset_id = OLD.id;
                END;
            """ % dict(table=table))

    def is_initialized(self):
        """Quickly test whether this database has been initialized."""
        # Test if database file exists
        if os.path.exists(self.db_path):
            return self.exists('sqlite_master',
                {'type': 'table', 'name': 'changeset'}
            )
        else:
            return False

    def process_db_errors(method):
        """Decorator that reformats some db errors"""
        def wrapper(self, *args, **kwargs):
            try:
                return method(self, *args, **kwargs)
            except Exception, e:
                if not self.is_initialized():
                    raise UninitializedRepositoryError
                else:
                    raise
        return wrapper

    def format_clauses(self, where_clauses=None):
        """Return (sql, parameters) for the specified clauses."""
        expressions = []
        parameters = []
        sql = ""
        # Compute sql for where_clauses
        if where_clauses is not None:
            for col, val in where_clauses.iteritems():
                # If value is None, use the IS NULL syntax
                if val is None:
                    expressions.append("%s IS NULL" % col)
                else:
                    expressions.append("%s = ?" % col)
                    parameters.append(val)
            if len(where_clauses) > 0:
                sql = "WHERE %s" % " AND ".join(expressions)
        return (sql, parameters)

    @process_db_errors
    def select(self, table, columns=None, where_clauses=None):
        """Return the results of the specified SELECT.
        
        `table` - the table name for the FROM clause of the SELECT statement
        `columns` - a list of column names (or expressions) to SELECT
        `where_clauses` - a dictionary of column-name/search-expression pairs
        for the WHERE clause of the SELECT statement
        
        """
        # SELECT FROM table WHERE a=? AND b=?
        where_sql, parameters = self.format_clauses(where_clauses)
        columns_sql = ", ".join(columns if columns is not None else ['*'])
        sql = "SELECT %s FROM %s %s" % (columns_sql, table, where_sql)
        log.debug("select sql: %s, %r" % (sql, parameters))
        # Execute SQL return results
        return self.db.execute(sql, parameters)
        
    @process_db_errors
    def exists(self, table, where_clauses=None):
        """Test if a record exists in `table` with the given conditions."""
        # Compute SQL for where_clauses
        results = self.select(table, where_clauses=where_clauses).fetchone()
        if results: 
            return True
        else:
            return False

    @process_db_errors
    def insert(self, table, column_clauses=None):
        """Perform INSERT on `table` with the given values.
        
        `table` - the name of the table to insert a record into
        `column_clauses` - a dictionary specifying column-name/value pairs for 
        this INSERT statement
        
        """
        # INSERT INTO table(column_a, column_b, ...) VALUES(?, ?, ...)
        if column_clauses is None:
            column_clauses = {}
        columns = column_clauses.keys()
        values = [column_clauses[c] for c in columns]
        sql = "INSERT INTO %s(%s) values(%s)" % (
            table,
            ", ".join(columns),
            ", ".join(['?' for v in values])
        )
        log.debug("insert sql: %s, %r" % (sql, values))
        return self.db.execute(sql, values)

    @process_db_errors
    def update(self, table, update_clauses, where_clauses=None):
        """Perform UPDATE on table with the given constraints."""
        # Compute sql for where_clauses
        where_sql, where_parameters = self.format_clauses(where_clauses)
        # Compute sql for update_clauses
        expressions = []
        parameters = []
        for col, val in update_clauses.iteritems():
            expressions.append("%s = ?" % col)
            parameters.append(val)
        sql = "UPDATE %s SET %s %s" % (
            table,
            ", ".join(expressions),
            where_sql
        )
        # Execute SQL return results
        return self.db.execute(sql, parameters + where_parameters)
    
    @process_db_errors
    def delete(self, table, where_clauses):
        """Perform DELETE on table with the given constraints."""
        # "DELETE FROM table WHERE column_a = ? AND column_b = ? AND ..."
        where_sql, parameters = self.format_clauses(where_clauses)
        sql = "DELETE FROM %s %s" % (table, where_sql)
        log.debug("delete sql: %s, %r" % (sql, parameters))
        return self.db.execute(sql, parameters)

    @process_db_errors
    def iterate_properties(self, path, max_changeset=None):
        """Return an iterator for properties on the specified path."""
        # If max_changeset wasn't specified, yield uncommitted changes first.
        uncommitted_propnames = []
        if max_changeset is None:
            uncommitted_changes = self.select('property', 
                ['propname', 'propval'],
                dict(changeset_id=None, path=path)
            )
            for propname, propval in uncommitted_changes:
                uncommitted_propnames.append(propname)
                yield (propname, propval)
        # Next look for properties committed on or before max_changeset
        changeset_clause = ""
        if max_changeset:
            changeset_clause = "AND m.changeset_id <= %s" % max_changeset
        sql = """
            SELECT propname, propval FROM property
            WHERE path = ? 
            AND changeset_id IS NOT NULL
            AND %d !=
                (SELECT status FROM property AS m
                 WHERE m.propname = property.propname
                 AND m.path = property.path
                 AND m.changeset_id IS NOT NULL
                 %s
                 ORDER BY m.changeset_id DESC LIMIT 1)
        """ % (DELETED, changeset_clause)
        for propname, propval in self.db.execute(sql, [path]):
            # Avoid yielding something twice
            if propname not in uncommitted_propnames:
                yield (propname, propval)

    def __property_results(self, propname, results, path, default=RAISE_ERR):
        """Internal helper method for get_property."""
        propval, status = results
        if status == DELETED:
            if default is RAISE_ERR:
                raise PropertyNotFound(propname, path)
            else:
                return default
        else:
            return propval

    @process_db_errors
    def get_property(self, name, path, default=RAISE_ERR, max_changeset=None):
        """Return the property value for path, or a default value."""
        # If max_changeset wasn't specified, return a uncommitted value first.
        if max_changeset is None:
            results = self.select('property', 
                ['propval', 'status'], 
                dict(changeset_id=None, path=path)
            ).fetchone()
            if results:
                return self.__property_results(name, results, path, default)
        # Otherwise look for the most recent value
        changeset_clause = ""
        if max_changeset:
            changeset_clause = "AND changeset_id <= %s" % max_changeset
        sql = """
            SELECT propval, status FROM property
            WHERE path = ? 
            AND propname = ?
            AND changeset_id IS NOT NULL
            %s
            ORDER BY changeset_id DESC LIMIT 1
        """ % changeset_clause
        results = self.db.execute(sql, [path, name]).fetchone()
        if results:
            return self.__property_results(name, results, path, default)
        
    @process_db_errors
    def delete_property(self, propname, path, changeset=None):
        """Record a property deletion on path."""
        # Get existing property value (raises error if nonexistent)
        propval = self.get_property(propname, path)
        status = DELETED
        self._change_property(propname, propval, path, changeset, status)
        
    @process_db_errors
    def has_property(self, propname, path, max_changeset=None):
        """Return whether the path has the specified property."""
        try:
            self.get_property(propname, path, max_changeset=max_changeset)
        except PropertyNotFound, e:
            return False
        else:
            return True
        
    @process_db_errors
    def set_property(self, propname, propval, path, changeset=None):
        """Record a property change for the specified path."""
        # Determine if this is a modification of an active property
        if self.has_property(propname, path, self.current_changeset):
            status = MODIFIED
        else:
            status = ADDED
        self._change_property(propname, propval, path, changeset, status)
    
    @process_db_errors
    def _change_property(self, propname, propval, path, changeset, status):
        """Workhorse for set_property and delete_property"""
        # Delete any uncommitted property changes for this property & path.
        self.delete('property',
            dict(propname=propname, path=path, changeset_id=None)
        )
        # Finally record the property change
        self.insert('property', {
            'propname': propname,
            'propval': propval,
            'path': path,
            'changeset_id': changeset,
            'status': status
        })
        
    @process_db_errors
    def commit_property_changes(self, path, changeset):
        """Commit all uncommitted property changes for the specified path."""
        self.update('property', dict(changeset_id=changeset), dict(path=path))

    @process_db_errors
    def get_active_hash(self, path):
        """Return the hash from the specified active_set record"""
        results = self.select(
            'active_set', columns=['hash'], where_clauses=dict(path=path)
        ).fetchone()
        if results is None:
            return None
        else:
            return results[0]

    @process_db_errors
    def get_active_fingerprint(self, path):
        """Return the fingerprint from the specified active_set record."""
        results = self.select(
            'active_set', 
            columns=['fingerprint'], 
            where_clauses=dict(path=path)
        ).fetchone()
        if results is None:
            return None
        else:
            return results[0]

    @process_db_errors
    def get_active_file_type(self, path):
        """Return the file_type from the specified active_set record."""
        results = self.select(
            'active_set', columns=['type'], where_clauses=dict(path=path)
        ).fetchone()
        if results is None:
            return None
        else:
            return results[0]

    @process_db_errors
    def get_previous_version(self, path, changeset):
        """Return the version of path that existed just before changeset"""
        sql = ("SELECT hash, fingerprint, type, status FROM modification "
               "WHERE path = ? AND changeset_id < ? "
               "ORDER BY changeset_id DESC LIMIT 1")
        return self.db.execute(sql, [path, changeset]).fetchone()

    @process_db_errors
    def get_current_changeset(self):
        """Return the current changeset"""
        results = self.select('changeset', columns=['MAX(id)']).fetchone()
        if results is None:
            return None
        else:
            return results[0]
    current_changeset = property(get_current_changeset)

    @process_db_errors
    def record_deleted(self, 
                       changeset, 
                       path, 
                       path_hash, 
                       fingerprint,
                       file_type, 
                       status):
        """Record a path deletion in the active_set and modification tables"""
        self.delete('active_set', {'path': path})
        self.record_change(
            changeset, path, path_hash, fingerprint, file_type, status
        )

    @process_db_errors
    def record_added(self, *args, **kwargs):
        """Record a path addition in the active_set and modification tables"""
        self.record_modified(*args, **kwargs)
                
    @process_db_errors
    def record_modified(self,
                        changeset,
                        path,
                        path_hash,
                        fingerprint,
                        file_type,
                        status):
        """Record a path modification in the active_set table"""
        # Replace the active_set record with the current info
        self.delete('active_set', dict(path=path))
        self.insert('active_set', {
            'path': path,
            'hash': path_hash,
            'fingerprint': fingerprint,
            'type': file_type
        })
        self.record_change(
            changeset, path, path_hash, fingerprint, file_type, status
        )

    @process_db_errors
    def record_change(self,
                      changeset,
                      path,
                      path_hash,
                      fingerprint,
                      file_type,
                      status):
        """Record a path modification to the modification table"""
        self.insert('modification', {
            'changeset_id': changeset,
            'path': path,
            'hash': path_hash,
            'fingerprint': fingerprint,
            'type': file_type,
            'status': status
        })