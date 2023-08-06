"""Application program interface (API)"""

import logging


from checkpoint.constants import RAISE_ERR
from checkpoint.error import (
    VersionError, CheckpointError, UninitializedMirrorError, 
    UninitializedRepositoryError
)
from checkpoint.repository import (
    Repository, Mirror, SUPPORTED_REPOSITORY_FORMAT, STATUS_CODES
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
    COMMANDS = [
        'mirror', 'refresh', 'forget', 'recover', 'proplist', 'propget'
    ]
    
    def __init__(self, destination_directory=None):
        self.destination_directory = destination_directory
        # Raise error if mirror_directory contains a repository
        if Repository.contains_repository(self.destination_directory):
            raise CheckpointError(
                "Can't run a Mirror command inside %r: "
                "this directory contains a Repository." % 
                self.destination_directory
            )
        # Instantiate Mirror object
        self._mirror = Mirror(self.destination_directory)

    def verify_mirror(method):
        """Decorator that raises an error if mirror isn't initialized."""
        def wrapper(self, *args, **kwargs):
            if not Mirror.contains_mirror(self.destination_directory):
                raise UninitializedMirrorError()
            return method(self, *args, **kwargs)
        return wrapper

    def mirror(self, source_directory=None):
        """Create a mirror of a Checkpoint directory."""
        self._mirror.mirror(source_directory)

    @verify_mirror
    def refresh(self):
        """Bring a mirror up-to-date."""
        self._mirror.refresh()

    @verify_mirror
    def forget(self):
        """Delete mirror configuration directory."""
        self._mirror.delete_mirror()

    @verify_mirror
    def recover(self):
        """Attempt to repair the Mirror."""
        self._mirror.recover()    

    @verify_mirror
    def propget(self, propname, paths):
        """Print the desired property values of the specified paths."""
        for path in paths:
            log.info("Property %r on %r:" % (propname, path))
            self._mirror.get_property(propname, path)

    @verify_mirror
    def proplist(self, paths):
        """Print a list of properties currently set on the specified paths."""
        # Get all the properties on all the paths
        data = dict.fromkeys(paths, {})
        for path in paths:
            for name, value in self._mirror.iterate_properties(path):
                data[path][name] = value
        # Print the properties grouped by path
        for path in paths:
            log.info("Properties on %r" % path)
            for k,v in data[path].iteritems():
                log.info("\t%s" % k)


class RepositoryManager(Common):
    """Checkpoint Repository public API"""
    # Specify which methods are CLI commands
    COMMANDS = ['watch', 'status', 'commit', 'revert', 'forget', 'recover',
                'propset', 'propget', 'propdel', 'proplist', 'move', 'copy']

    def __init__(self, directory=None):
        self.directory = directory # should/will contain repository
        # Raise error if directory contains a mirror
        if Mirror.contains_mirror(self.directory):
            raise CheckpointError(
                "Can't run a Repository command inside %r: "
                "this directory contains a Mirror." % 
                self.directory
            )
        # Instantiate Repository object
        self._repository = Repository(self.directory)

    def verify_repository(method):
        """Decorator that ensures a compatible, initialized repository."""
        def wrapper(self, *args, **kwargs):
            # Verify repository was initialized (cache results!)
            if not getattr(self, '_repository_initialized', False):
                if not Repository.contains_repository(self.directory):
                    raise UninitializedRepositoryError()
                self._repository_initialized = True
            # Validate repository format (cache results!)
            if not hasattr(self, '_repository_format'):
                self._repository_format = self._repository.repository_format
                if self._repository_format != SUPPORTED_REPOSITORY_FORMAT:
                    raise VersionError()
            return method(self, *args, **kwargs)
        return wrapper

    @verify_repository
    def commit(self, paths=None):
        """Commit any unsaved changes to a new changeset."""
        self._repository.commit(paths)

    @verify_repository
    def copy(self, source, destination):
        """Copy file along with its properties."""
        self._repository.copy(source, destination)

    @verify_repository
    def delete_property(self, propname, path):
        """Delete a property from the specified relative path."""
        self._repository.delete_property(propname, path)

    @verify_repository
    def forget(self):
        """Delete repository, leaving directory as-is."""
        self._repository.delete_repository()
        self._repository_initialized = False

    @verify_repository
    def get_property(self, propname, path, default=RAISE_ERR):
        """Get the property value for the specified relative path."""
        return self._repository.get_property(propname, path, default)
    
    @verify_repository
    def iterate_changes(self, paths=None):
        """Return an iterable of all changes since last commit."""
        for change in self._repository.iterate_changes(paths):
            yield change

    @verify_repository
    def iterate_properties(self, paths):
        """Return an iterable of properties on the specified relative path."""
        for path in paths:
            for prop in self._repository.iterate_properties(path):
                propname, propval = prop
                yield (propname, propval, path)

    @verify_repository
    def move(self, source, destination):
        """Move/Rename file along with its properties."""
        self._repository.move(source, destination)

    @verify_repository
    def propdel(self, propname, paths):
        """Remove a property from the specified paths."""
        for path in paths:
            self._repository.delete_property(propname, paths)

    @verify_repository
    def propget(self, propname, paths):
        """Print the desired property values of the specified paths."""
        for path in paths:
            log.info("Property %r on %r:" % (propname, path))
            self._repository.get_property(propname, path)

    @verify_repository
    def proplist(self, paths):
        """Print a list of properties currently set on the specified paths."""
        # Get all the properties on all the paths
        data = dict.fromkeys(paths, {})
        for path in paths:
            for name, value in self._repository.iterate_properties(path):
                data[path][name] = value
        # Print the properties grouped by path
        for path in paths:
            log.info("Properties on %r" % path)
            for k,v in data[path].iteritems():
                log.info("\t%s" % k)

    @verify_repository
    def propset(self, propname, propval, paths):
        """Set property values on the specified paths."""
        for path in paths:
            self._repository.set_property(propname, propval, path)

    @verify_repository
    def recover(self):
        """Attempt to repair the Repository."""
        self._repository.recover()

    @verify_repository
    def revert(self, desired_changeset=None):
        """Revert to a previous changeset."""
        self._repository.revert(desired_changeset)
    
    @verify_repository
    def set_property(self, propname, propval, path):
        """Set a property value on the specified relative path."""
        self._repository.set_property(propname, propval, path)
    
    @verify_repository
    def status(self, paths=None):
        """Print a list of changes since last commit."""
        log.info(
            "Printing status of directory: %r" % self._repository.directory
        )
        current_changeset = self._repository.current_changeset
        log.info("Changes since changeset %s..." % str(current_changeset))
        for change in self._repository.iterate_changes(paths=paths):
            path, path_hash, fingerprint, file_type, status = change
            log.info("%s\t%s" % (STATUS_CODES[status], path))
    
    def watch(self):
        """Create repository and commit all existing files."""
        self._repository.initialize()
        self.commit()