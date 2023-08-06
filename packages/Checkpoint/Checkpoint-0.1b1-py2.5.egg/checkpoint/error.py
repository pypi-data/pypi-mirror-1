"""Error classes for Checkpoint"""

from textwrap import dedent
from traceback import format_stack

__all__ = [
    'NoChanges', 'CheckpointBug', 'CheckpointError', 'RepositoryLocked', 
    'NotFound', 'InvalidCommand', 'FileError', 'RepositoryError', 
    'UnsupportedFileType',
]

class NoChanges(Warning):
    """Indicates no changes were made to repository or directory"""

class CheckpointBug(Exception):
    """Error indicates a bug in the checkpoint API"""
    def __init__(self, message=""):
        super(CheckpointBug, self).__init__()
        self.message = (
            "Unrecoverable Error!\n" + message + "\n" +
            ("Traceback (most recent call last):\n%s" % format_stack()) +
            dedent("""
                This could be a bug in Checkpoint.
                Please report this bug as described at
                http://something something something....
            """)
        )

class CheckpointError(Exception):
    """Base class for anticipated errors in the checkpoint package"""
    def __init__(self, *args, **kwargs):
        super(CheckpointError, self).__init__(*args, **kwargs)
        if not str(self):
            self.message = dedent(self.__class__.__doc__)

class RepositoryLocked(CheckpointError):
    """Repository is locked."""
    def __init__(self):
        super(RepositoryLocked, self).__init__()
        self.message = dedent("""
            --------------------------------------------------------------
            !!! Repository is Locked! !!!
        
            This could be because another process has the repository open.
    
            Most likely though, it means the last repository command has 
            failed or crashed, leaving the repository dirty.  Try the 
            'cleanup' command to attempt to fix the repository.  If that 
            doesn't work, manual crash-recovery may be the only option.  
            Check the documentation for more information.
            --------------------------------------------------------------
            
        """)

class NotFound(CheckpointError):
    """Specified file or directory does not exist"""
    def __init__(self, path):
        super(NotFound, self).__init__()
        self.message = "File or directory not found: %r" % path
        
class InvalidCommand(CheckpointError):
    """Not a valid Checkpoint command"""

class FileError(CheckpointError):
    """File operation error - error during rm, copy, mv, etc"""
    
class RepositoryError(CheckpointError):
    """Repository operation error - error during read, write, or create"""
    
class UnsupportedFileType(CheckpointError):
    """Unsupported file type (link, socket, pipe, device) was encountered"""
    def __init__(self, path):
        super(UnsupportedFileType, self).__init__()
        self.message = "Unsupported file type: %r" % path