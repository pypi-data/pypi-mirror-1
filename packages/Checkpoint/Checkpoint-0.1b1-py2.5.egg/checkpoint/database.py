"""Database abstraction layer"""

import os
import sqlite3
import logging

from checkpoint.error import *

__all__ = ['Database']

log = logging.getLogger("checkpoint")

class Database(object):
    """Context Manager and Wrapper class for all your database needs."""
    def __init__(self, repository_dir):
        super(Database, self).__init__()
        self.dbpath = self.get_path(repository_dir)
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
                self._db = sqlite3.Connection(self.dbpath)
                # self._db.row_factory = sqlite3.Row
        except sqlite3.OperationalError, e:
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
            CREATE TABLE modification (
                path TEXT NOT NULL, 
                hash TEXT DEFAULT NULL,
                type INTEGER NOT NULL,
                status INTEGER NOT NULL,
                changeset_id INTEGER NOT NULL
                    CONSTRAINT fk_changeset_id
                        REFERENCES changeset(id) 
                        ON DELETE CASCADE
            );
            CREATE TABLE active_set (
                path TEXT NOT NULL PRIMARY KEY,
                hash TEXT DEFAULT NULL,
                type INTEGER NOT NULL
                
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

    def __format_clauses(self, where_clauses=None):
        """Return (sql, parameters) for the specified WHERE clauses"""
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

    def select(self, table, columns=None, where_clauses=None):
        """Return the results of the specified SELECT"""
        # SELECT FROM table WHERE a=? AND c=?
        (where_sql, parameters) = self.__format_clauses(where_clauses)
        columns_sql = ", ".join(columns if columns is not None else ['*'])
        sql = "SELECT %s FROM %s %s" % (columns_sql, table, where_sql)
        log.debug("select sql: %s, %r" % (sql, parameters))
        # Execute SQL return results
        return self.db.execute(sql, parameters)

    def exists(self, table, where_clauses=None):
        """Test if a record exists with the given conditions"""
        # Compute SQL for where_clauses
        results = self.select(table, where_clauses=where_clauses).fetchone()
        if results: 
            return True
        else:
            return False

    def insert(self, table_name, column_values):
        """Perform INSERT on table with the given values"""
        # INSERT INTO table(column_a, column_b, ...) VALUES(?, ?, ...)
        columns = column_values.keys()
        values = [column_values[c] for c in columns]
        sql = "INSERT INTO %s(%s) values(%s)" % (
            table_name,
            ", ".join(columns),
            ", ".join(['?' for v in values])
        )
        log.debug("insert sql: %s, %r" % (sql, values))
        return self.db.execute(sql, values)

    def delete(self, table, where_clauses):
        """Perform DELETE on table with the given constraints"""
        # "DELETE FROM table WHERE column_a = ? AND column_b = ? AND ..."
        (where_sql, parameters) = self.__format_clauses(where_clauses)
        sql = "DELETE FROM %s %s" % (table, where_sql)
        log.debug("delete sql: %s, %r" % (sql, parameters))
        return self.db.execute(sql, parameters)
        
    def get_active_hash(self, path):
        """Return the hash from the specified active_set record"""
        results = self.select(
            'active_set', columns=['hash'], where_clauses=dict(path=path)
        ).fetchone()
        if results is None:
            return None
        else:
            return results[0]

    def get_active_file_type(self, path):
        """Return the file_type from the specified active_set record"""
        results = self.select(
            'active_set', columns=['type'], where_clauses=dict(path=path)
        ).fetchone()
        if results is None:
            return None
        else:
            return results[0]

    def get_previous_version(self, path, path_hash, changeset):
        """Return the version of path that existed just before changeset"""
        sql = ("SELECT hash, type, status FROM modification "
               "WHERE path = ? AND changeset_id < ? "
               "ORDER BY changeset_id DESC LIMIT 1")
        results = self.db.execute(sql, [path, changeset]).fetchone()
        return results

    def get_current_changeset(self):
        """Return the current changeset"""
        results = self.select('changeset', columns=['MAX(id)']).fetchone()
        if results is None:
            return None
        else:
            return results[0]
    current_changeset = property(get_current_changeset)

    def record_added(self, changeset, path, path_hash, file_type, status):
        """Record a path addition in the active_set and modification tables"""
        # Discourage duplicate paths in active_set
        self.delete('active_set', dict(path=path))
        self.insert('active_set', 
            {'path': path, 'hash': path_hash, 'type': file_type}
        )
        self.record_change(changeset, path, path_hash, file_type, status)

    def record_deleted(self, changeset, path, path_hash, file_type, status):
        """Record a path deletion in the active_set and modification tables"""
        self.delete('active_set', 
            {'path': path, 'hash': path_hash, 'type': file_type}
        )
        self.record_change(changeset, path, path_hash, file_type, status)
                
    def record_modified(self, changeset, path, path_hash, file_type, status):
        """Record a file modification in the active_set table"""
        # Replace the active_set record with the current info
        self.delete('active_set', dict(path=path))
        self.insert('active_set', 
            {'path': path, 'hash': path_hash, 'type': file_type}
        )
        self.record_change(changeset, path, path_hash, file_type, status)

    def record_change(self, changeset, path, path_hash, file_type, status):
        """Record a path modification to the modification table"""
        self.insert('modification', {
            'path': path,
            'status': status,
            'hash': path_hash,
            'type': file_type,
            'changeset_id': changeset
        })