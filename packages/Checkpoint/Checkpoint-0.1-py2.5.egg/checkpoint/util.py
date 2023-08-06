"""Utility methods and constants"""

from __future__ import with_statement

import os
import fcntl
import pickle
import hashlib
from fnmatch import fnmatch

__all__ = [
    'sha1_hash', 'matches_any_pattern', 'filter_all_patterns', 
    'ascending_length', 'descending_length', 'filter_duplicates',
    'PickleProperty', 'acquire_lock', 'release_lock'
]

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

def filter_duplicates(sequence):
    """Return sequence with duplicates removed.  Preserves order."""
    # Thanks to Dave Kirby for this recipe
    seen = set()
    return [x for x in sequence if x not in seen and not seen.add(x)]

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
    
class PickleProperty(object):
    """Descriptor that gets/sets file data"""
    def __init__(self, path_getter):
        self.path_getter = path_getter
    
    def __get__(self, instance, owner):
        """Return the data from the file."""
        path = self.path_getter(instance)
        try:
            with open(path, 'rb') as f:
                return pickle.load(f)
        except (OSError, IOError), e:
            raise AttributeError("Could not read file %r: %s" % (path, e))
    
    def __set__(self, instance, value):
        """Create the data file if necesary, and store data into it."""
        path = self.path_getter(instance)
        try:
            with open(path, 'wb') as f:
                pickle.dump(value, f, -1) # pickle using highest protocol
        except (OSError, IOError), e:
            raise AttributeError("Could not create file %r: %s" % (path, e))
            
def acquire_lock(lockfile_path, LockedException):
    """Acquire and return a lock using the given lockfile as the semaphore."""
    # ALL PROGRAMMERS PLEASE READ: 
    # This code uses fcntl.lockf, which is POSIX and NFS compatible 
    # (unlike flock) but it has the consequence that the file lock 
    # will silently be removedwhen *ANY* file descriptor to this file 
    # is closed, so be careful to close those descriptors only after 
    # you are ready to unlock the file.

    # Open lockfile for appending (so it's created if non-existent)
    try:
        f = open(lockfile_path, 'a')
    except (OSError, IOError), e:
        raise FileError("Could not create/open lockfile %r: %s" % 
            (lockfile_path, e)
        )

    # Lockfile has been opened, so attempt to get an exclusive lock 
    # on the lockfile.
    try:
        fcntl.lockf(f, fcntl.LOCK_EX|fcntl.LOCK_NB)
    except IOError, e:
        # If lockfile couldn't be acquired (another [possibly stale] 
        # process has it), raise error and proceed no further.
        raise LockedException()

    # Lockfile is opened and locked.  Read contents of lockfile to 
    # determine if there was a recent crash (and thus a stale pid in 
    # the lockfile)
    try:
        f_readonly = open(lockfile_path, 'r')
        stale_pid = f_readonly.readline()
    except (OSError, IOError), e:
        raise FileError("Could not read from lockfile %r: %s" % 
            (lockfile_path, e)
        )

    # If lockfile is empty, write the current PID to the lockfile.
    if not stale_pid:
        f.write(str(os.getpid()))
        # Flush OS file buffers to hard drive
        f.flush()
        # Flush hard drive buffers to disk (on OS-es that support it)
        if hasattr(fcntl, 'F_FULLFSYNC'):  
            fcntl.fcntl(f, fcntl.F_FULLFSYNC)
    else:
        # Stale PID detected, another process must have crashed 
        # (leaving the lockfile there).  Raise an error explaining 
        # how to recover.
        raise LockedException()
    
    # Return the lock
    class Lock(object):
        pass
    lock = Lock()
    lock.lockfile = f
    lock.lockfile_readonly = f_readonly
    lock.lockfile_path = lockfile_path
    return lock

def release_lock(lock):
    """Release the lock."""
    # Unlock and remove the lockfile
    try:
        fcntl.lockf(lock.lockfile, fcntl.LOCK_UN)
        lock.lockfile.close()
        lock.lockfile_readonly.close()
        os.remove(lock.lockfile_path)
    except (OSError, IOError), e:
        raise FileError("Could not remove lockfile %r: %s" % 
            (lock.lockfile_path, e)
        )