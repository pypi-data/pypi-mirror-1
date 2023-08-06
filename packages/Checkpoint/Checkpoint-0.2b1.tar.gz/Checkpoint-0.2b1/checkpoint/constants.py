"""Constants"""

__all__ = [
    'NO_CHANGE', 'ADDED', 'DELETED', 'MODIFIED', 'FILE', 'DIRECTORY', 'LINK',
    'RAISE_ERR', 'MOVED'
]

# Special flag that indicates if error should be suppressed
RAISE_ERR = object()

NO_CHANGE = 0
MODIFIED = 1
ADDED = 2
DELETED = 3

FILE = 0
DIRECTORY = 1
LINK = 2