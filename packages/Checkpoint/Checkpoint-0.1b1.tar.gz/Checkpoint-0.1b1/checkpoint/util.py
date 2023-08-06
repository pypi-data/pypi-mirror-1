"""Utility methods and constants"""
from __future__ import with_statement

import os
import hashlib
from fnmatch import fnmatch

__all__ = ['sha1_hash', 'matches_any_pattern', 'filter_all_patterns',
           'ascending_length', 'descending_length']

def ascending_length(x, y):
    return len(x) - len(y)

def descending_length(x, y):
    return len(y) - len(x)

def filter_all_patterns(paths, patterns):
    """Return only those paths that match no patterns"""
    return [p for p in paths if not matches_any_pattern(p, patterns)]

def matches_any_pattern(path, patterns):
    """Test if path matches any of the supplied patterns (ex: '*.jpg')"""
    return any(
        fnmatch(path, pattern) for pattern in patterns
    )

def sha1_hash(path):
    """Return a sha1 hash of path.
    
    For regular files, a sha1 hash of the data is returned.
    For directories, a sha1 hash of the directory name is returned.
    For links, a sha1 hash of the target path name is returned.
    For unsupported file types, None is returned.
    
    """
    h = hashlib.sha1()
    if os.path.islink(path):
        target = os.path.realpath(path)
        h.update(target)
    elif os.path.isdir(path):
        h.update(path)
    elif os.path.isfile(path):
        with open(path, 'rb') as f:
            hash_buffer_size = 1024
            while True:
                data = f.read(hash_buffer_size)
                if data:
                    h.update(data)
                else:
                    break
    else:
        return None
    return h.hexdigest()