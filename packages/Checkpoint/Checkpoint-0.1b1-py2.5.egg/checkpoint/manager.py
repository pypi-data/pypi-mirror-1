"""Top-level abstraction layer, for use in Command-Line Interface utility"""

import os
import logging

from checkpoint.error import *
from checkpoint.repository import Repository, STATUS_CODES

log = logging.getLogger("checkpoint")
    
class CheckpointManager(object):
    """Checkpoint management class"""
    COMMANDS = ['watch', 'status', 'commit', 'revert', 'forget', 'recover']
    
    def __init__(self, directory=None):
        super(CheckpointManager, self).__init__()
        
        # Initialize a Repository manager
        self.directory = os.path.abspath(directory)
        self.repository = Repository(self.directory)    

    def dispatch(self, command, options):
        """Dispatch to specfied command (Useful for CLI programs)."""
        if command not in self.__class__.COMMANDS:
            raise InvalidCommand("Unknown command: '%s'" % command)
        else:
            method = getattr(self, command)
            if command == 'revert':
                return method(options.changeset)
            else:
                return method()

    def forget(self):
        """Permanently delete repository."""
        self.repository.delete_repository()

    def watch(self):
        """Create repository and commit all existing files."""
        self.repository.initialize()
        self.commit()
        
    def status(self):
        """Print a list of changes since last commit."""
        log.info("Printing status of directory: %r" % self.directory)
        # Raise an error if repository is locked
        if self.repository.is_locked():
            raise RepositoryLocked()
        # Print changes to stdout.
        current_changeset = self.repository.current_changeset
        log.info("Changes since changeset %s..." % str(current_changeset))
        for (path, path_hash, file_type, status) in self.repository.changes():
            log.info("%s\t%s" % (STATUS_CODES[status], path))

    def commit(self):
        """Commit any unsaved changes to a new changeset."""
        self.repository.commit()

    def revert(self, desired_changeset=None):
        """Revert to a previous changeset."""
        self.repository.revert(desired_changeset)
        
    def recover(self):
        """Attempt to repair directory and restore any missing files."""
        self.repository.recover()
        