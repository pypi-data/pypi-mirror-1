"""Checkpoint application program interface (API)"""

import logging

from checkpoint.repository import (
    Repository, Mirror, SUPPORTED_REPOSITORY_FORMAT
)
from checkpoint.error import (
    VersionError, CheckpointError, UninitializedMirrorError, 
    UninitializedRepositoryError
)

__all__ = ['MirrorManager', 'RepositoryManager']

log = logging.getLogger("checkpoint")

class Common(object):
    def dispatch(self, command, *args, **kwargs):
        """Dispatch to specfied command (Useful for CLI programs)."""
        if command not in self.__class__.COMMANDS:
            raise InvalidCommand("Unknown command: '%s'" % command)
        else:
            method = getattr(self, command)
            method(*args, **kwargs)

class MirrorManager(Common):
    """Checkpoint Mirror public API"""
    COMMANDS = ['mirror', 'refresh', 'forget', 'recover']
    
    def __init__(self, destination_directory=None):
        self.destination_directory = destination_directory

    def uses_mirror(method):
        """Decorator that adds a Mirror object to `self` as needed."""
        def wrapper(self, *args, **kwargs):
            # Raise error if mirror_directory contains a repository
            if Repository.contains_repository(self.destination_directory):
                raise CheckpointError(
                    "Can't run a Mirror command inside %r: "
                    "this directory contains a Repository." % 
                    self.destination_directory
                )
            # Instantiate Mirror object if necessary
            if not hasattr(self, '_mirror'):
                self._mirror = Mirror(self.destination_directory)
            return method(self, *args, **kwargs)
        return wrapper

    def requires_mirror(method):
        """Decorator that raises an error if mirror isn't initialized."""
        def wrapper(self, *args, **kwargs):
            if not Mirror.contains_mirror(self.destination_directory):
                raise UninitializedMirrorError()
            return method(self, *args, **kwargs)
        return wrapper

    @uses_mirror
    def mirror(self, source_directory=None):
        """Create a mirror of a Checkpoint directory."""
        self._mirror.mirror(source_directory)

    @uses_mirror
    @requires_mirror
    def refresh(self):
        """Bring a mirror up-to-date."""
        self._mirror.refresh()

    @uses_mirror
    @requires_mirror
    def forget(self):
        """Delete mirror configuration directory."""
        self._mirror.delete_mirror()

    @uses_mirror
    @requires_mirror
    def recover(self):
        """Attempt to repair the Mirror."""
        self._mirror.recover()    

class RepositoryManager(Common):
    """Checkpoint Repository public API"""
    COMMANDS = ['watch', 'status', 'commit', 'revert', 'forget', 'recover']
    
    def __init__(self, directory=None):
        self.directory = directory # should/will contain repository

    def version_check(method):
        """Decorator that ensures a compatible repository format."""
        def wrapper(self, *args, **kwargs):
            repository_format = self._repository.repository_format
            if repository_format != SUPPORTED_REPOSITORY_FORMAT:
                raise VersionError()
            return method(self, *args, **kwargs)
        return wrapper
    
    def uses_repository(method):
        """Decorator that adds a Repository object to `self` as needed."""
        def wrapper(self, *args, **kwargs):
            # Raise error if directory contains a mirror
            if Mirror.contains_mirror(self.directory):
                raise CheckpointError(
                    "Can't run a Repository command inside %r: "
                    "this directory contains a Mirror." % 
                    self.directory
                )
            # Instantiate Repository object if necessary
            if not hasattr(self, '_repository'):
                self._repository = Repository(self.directory)
            return method(self, *args, **kwargs)
        return wrapper

    def requires_repository(method):
        """Decorator that raises an error if repository isn't initialized."""
        def wrapper(self, *args, **kwargs):
            if not Repository.contains_repository(self.directory):
                raise UninitializedRepositoryError()
            return method(self, *args, **kwargs)
        return wrapper

    @uses_repository
    @requires_repository
    @version_check
    def forget(self):
        """Delete repository, leaving directory as-is."""
        self._repository.delete_repository()

    @uses_repository
    def watch(self):
        """Create repository and commit all existing files."""
        self._repository.initialize()
        self.commit()

    @uses_repository
    @requires_repository
    @version_check
    def status(self):
        """Print a list of changes since last commit."""
        self._repository.print_changes()

    @uses_repository
    @requires_repository
    @version_check
    def iter_changes(self):
        """Return an iterable of all changes since last commit."""
        for change in self._repository.iter_changes(): 
            yield change

    @uses_repository
    @requires_repository
    @version_check
    def commit(self):
        """Commit any unsaved changes to a new changeset."""
        self._repository.commit()

    @uses_repository
    @requires_repository
    @version_check
    def revert(self, desired_changeset=None):
        """Revert to a previous changeset."""
        self._repository.revert(desired_changeset)

    @uses_repository
    @requires_repository
    @version_check
    def recover(self):
        """Attempt to repair the Repository."""
        self._repository.recover()