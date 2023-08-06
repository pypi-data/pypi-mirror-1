"""Error classes"""

from textwrap import dedent
from traceback import format_stack

__all__ = [
    'NoChanges', 'CheckpointBug', 'CheckpointError', 'RepositoryLocked', 
    'NotFound', 'InvalidCommand', 'FileError', 'RepositoryError', 
    'UnsupportedFileType', 'VersionError', 'UninitializedRepositoryError',
    'MirrorLocked', 'PropertyNotFound'
]

class CheckpointError(Exception):
    """Base class for anticipated errors in the checkpoint package"""
    def __init__(self, message=None):
        self.message = message
        if self.message is None:
            self.message = dedent(self.__class__.__doc__)    
    def __str__(self):
        return getattr(self, 'message', '')

class CheckpointBug(CheckpointError):
    """Error indicates a bug in the checkpoint API"""
    def __init__(self, message=""):
        self.message = (
            "Unrecoverable Error!\n" + message + "\n" +
            ("Traceback (most recent call last):\n%s" % format_stack()) +
            dedent("""
                This could be a bug in Checkpoint.
                Please report this bug as described at
                http://something something something....
            """)
        )
    def __str__(self):
        return getattr(self, 'message', '')

class RepositoryLocked(CheckpointError):
    """Repository is locked."""
    def __init__(self):
        self.message = dedent("""
            --------------------------------------------------------------
            !!! Repository is Locked! !!!
        
            This could be because another process has the repository open.
    
            Most likely though, it means the last repository command has 
            failed or crashed, leaving the repository dirty.  Try the 
            'recover' command to attempt to fix the repository.  If that 
            doesn't work, manual crash-recovery may be the only option.  
            Check the documentation for more information.
            --------------------------------------------------------------
            
        """)

class MirrorLocked(CheckpointError):
    """Mirror is locked."""
    def __init__(self):
        self.message = dedent("""
            --------------------------------------------------------------
            !!! Mirror is Locked! !!!

            This could be because another process has the mirror open.

            Most likely though, it means the last mirror command has 
            failed or crashed, leaving the mirror dirty.  Try the 
            'recover' command to attempt to fix the mirror.  If that 
            doesn't work, manual crash-recovery may be the only option.  
            Check the documentation for more information.
            --------------------------------------------------------------
            
        """)

class NoChanges(CheckpointError):
    """Indicates no changes were made to repository or directory"""

class NotFound(CheckpointError):
    """Specified file or directory does not exist."""
    def __init__(self, path):
        self.message = "File or directory not found: %r" % path

class PropertyNotFound(CheckpointError):
    """Specified property does not exist on specified path."""
    def __init__(self, propname, path):
        self.message = "Property %r not found on %r" % (propname, path)

class InvalidCommand(CheckpointError):
    """Specified command is not a valid Checkpoint command."""

class FileError(CheckpointError):
    """File operation error - error during rm, copy, mv, etc."""
    
class RepositoryError(CheckpointError):
    """Repository operation error - error during read, write, or create."""

class UninitializedRepositoryError(CheckpointError):
    """Repository must be initialized for this operation to succeed."""

class UninitializedMirrorError(CheckpointError):
    """Mirror must be initialized for this operation to succeed."""
    
class UnsupportedFileType(CheckpointError):
    """Unsupported file type (link, socket, pipe, device) was encountered."""
    def __init__(self, path):
        self.message = "Unsupported file type: %r" % path

class VersionError(CheckpointError):
    """Repository format is incompatible with this version of Checkpoint."""