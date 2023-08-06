"""command-line interface (CLI)"""

import os 
import sys
import logging
from textwrap import dedent
from optparse import OptionParser

from checkpoint.repository import Repository, Mirror
from checkpoint.manager import MirrorManager, RepositoryManager
from checkpoint.release import DESCRIPTION, VERSION, URL
from checkpoint.error import (
    CheckpointError, UninitializedRepositoryError, UninitializedMirrorError
)

__all__ = ['mirror', 'repository']

log = logging.getLogger("checkpoint")

SUCCESS = 0
ERROR = 1

crash_recovery_confirmation = dedent("""
    --------------------------------------------------------------
    !!! Confirm Crash Recovery! !!!

    You have selected crash recovery.  This process will move all
    files to a new crash recovery directory and then one-by-one 
    restore your files from the good copies in the repository.

    If this process is interrupted for any reason, you can try 
    recovery again to attempt to restore your files.  If recovery
    still does not finish successfully, or if it finishes successfully
    but you still appear to be missing files, you may have to try 
    manual crash-recovery.  See the documentation for more details.
    --------------------------------------------------------------

""")    

def configure_loggers():
    # Configure logging.  Since this is a command-line-interface (CLI),
    # logging goes to stdout, and log level is set to INFO so user can see
    # what the CLI is doing.  Note: log is defined at the module level
    log_level = logging.INFO
    try:
        if int(os.environ['CHECKPOINT_DEBUG']) == 1:
            log_level = logging.DEBUG
    except KeyError:
        pass
    log.setLevel(log_level) 
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter('%(message)s'))
    log.addHandler(handler)    

def find_mirror(starting_dir):
    """Starting at starting_dir, walk up until a Mirror is found."""
    d = starting_dir
    while d and not Mirror.contains_mirror(d):
        parent_dir = os.path.split(d)[0]
        # Break when root is reached
        if d == parent_dir:
            break
        else:
            d = parent_dir
    if Mirror.contains_mirror(d):
        return d
    else:
        message="%r is not part of a Checkpoint Mirror" % starting_dir
        raise UninitializedMirrorError(message)

def mirror(argv=sys.argv):
    usage = """
        usage:  %(prog)s <command> [args]
        Checkpoint Mirror command-line utility, version %(version)s

        Most commands accept a directory argument.  If this argument is not
        specified, the current directory will be used by default.
        
        Mirror Commands:
            forget [<dir>]                  Delete mirror configuration
            mirror <source-dir> <dest-dir>  Mirror a checkpoint directory
            propget NAME PATH...            Get property values from files
            proplist PATH...                List all properties on files
            recover [<dir>]                 Recover after a crash or failure
            refresh [<dir>]                 Bring a mirror up to date

    
        %(description)s
        For additional information, see %(url)s
    """ % dict(
        prog=os.path.basename(argv[0]),
        description=DESCRIPTION,
        version=VERSION,
        url=URL
    )
    usage = dedent(usage)
    configure_loggers()

    # Determine Checkpoint command
    try:
        command = argv[1]
        if command not in MirrorManager.COMMANDS:
            raise ValueError
    except (IndexError, ValueError):
        log.error(usage)
        return ERROR
    
    # Determine command arguments
    kw = dict()

    # Determine directories
    destination_directory = None
    if command == 'mirror':
        if len(argv) == 3:
            kw['source_directory'] = argv[2]
            destination_directory = os.getcwd()
        elif len(argv) == 4:
            kw['source_directory'] = argv[2]
            destination_directory = argv[3]
        else:
            log.error(usage)
            return ERROR
    elif command in ['refresh', 'forget', 'recover']:
        if len(argv) == 3:
            destination_directory = argv[2]
    if destination_directory is None:
        try:
            destination_directory = find_mirror(os.getcwd())
        except UninitializedMirrorError, e:
            log.error(e)
            return ERROR

    # If 'recover' was requested, confirm this with the user
    if command == 'recover':
        log.info(crash_recovery_confirmation)
        choice = raw_input("Proceed with crash recovery [yes/no]: ")
        if choice.lower() != "yes":
            log.info("Crash recovery was cancelled.")
            return SUCCESS

    # Determine arguments for propget/proplist commands
    if command == 'propget':
        if len(argv) < 4:
            log.error(usage)
            return ERROR
        else:
            kw['propname'] = argv[2]
            kw['paths'] = argv[3:]
    elif command == 'proplist':
        if len(argv) < 3:
            log.error(usage)
            return ERROR
        else:
            kw['paths'] = argv[2:]

    # Convert paths to the expected format (abspath or relpath)
    destination_directory = os.path.abspath(
        os.path.normpath(destination_directory)
    )
    if 'source_directory' in kw:
        kw['source_directory'] = os.path.abspath(
            os.path.normpath(kw['source_directory'])
        )
    if 'paths' in kw:
        relpaths = []
        for path in kw['paths']:
            abspath = os.path.abspath(os.path.normpath(path))
            relpath = abspath[len(directory):].lstrip(os.sep)
            relpaths.append(relpath)
        kw['paths'] = relpaths

    # Dispatch to command handler
    try:
        manager = MirrorManager(destination_directory=destination_directory)
        return manager.dispatch(command, **kw)
    except CheckpointError, e:
        log.error(e)
        return ERROR

def find_checkpoint_dir(starting_dir):
    """Starting at starting_dir, walk up until a Checkpoint dir is found."""
    d = starting_dir
    while d and not Repository.contains_repository(d):
        parent_dir = os.path.split(d)[0]
        # Break when root is reached
        if d == parent_dir:
            break
        else:
            d = parent_dir
    if Repository.contains_repository(d):
        return d
    else:
        message="%r is not part of a Checkpoint Directory" % starting_dir
        raise UninitializedRepositoryError(message)

def repository(argv=sys.argv):
    usage = """
        usage:  %(prog)s <command> [options] [args]
        Checkpoint command-line utility, version %(version)s

        Most commands accept a directory argument.  If this argument is not
        specified, the current directory will be used by default.

        Repository Commands:
        
            commit [PATH ...]           Save all changes since last commit
            copy SRC DST                Duplicate a file and its properties
            forget [DIR]                Delete saved history of changes
            move SRC DST                Move/Rename a file and its properties
            propdel NAME PATH...        Delete property from files
            propget NAME PATH...        Get property values from files
            proplist PATH...            List all properties on files
            propset NAME VAL PATH...    Set property values on files
            recover [DIR]               Recover after a crash or failure
            revert -c CHANGESET [DIR]   Revert directory to previous changeset            
            status [PATH ...]           List all changes since last commit
            watch [DIR]                 Watch directory for changes

        %(description)s
        For additional information, see %(url)s
    """ % dict(
        prog=os.path.basename(argv[0]),
        description=DESCRIPTION,
        version=VERSION,
        url=URL
    )
    usage = dedent(usage)    
    configure_loggers()

    # Determine Checkpoint command
    try:
        command = argv[1]
        if command not in RepositoryManager.COMMANDS:
            raise ValueError
    except (IndexError, ValueError):
        log.error(usage)
        return ERROR

    # Determine command line options
    kw = dict()

    # If 'recover' was requested, confirm this with the user
    if command == 'recover':
        log.info(crash_recovery_confirmation)
        choice = raw_input("Proceed with crash recovery [yes/no]: ")
        if choice.lower() != "yes":
            log.info("Crash recovery was cancelled.")
            return ERROR

    # If 'revert' was selected, determine optional specified changeset
    if command == 'revert':
        parser = OptionParser()
        parser.add_option('-c', dest="changeset", default=None, type='int')
        try:
            (options, extra_args) = parser.parse_args(argv[2:])
        except:
            log.error(usage)
            return ERROR
        kw['desired_changeset'] = options.changeset

    # Determine Checkpoint dir
    directory = None
    if command == 'watch':
        if len(argv) == 3:
            directory = argv[2]
        else:
            directory = os.getcwd()
    elif command in ['forget', 'recover', 'revert']:
        if len(argv) == 3:
            directory = argv[2]
    if directory is None:
        try:
            directory = find_checkpoint_dir(os.getcwd())
        except UninitializedRepositoryError, e:
            log.error(e)
            return ERROR
        
    #  Some commands take an optional list of path names
    if command in ['status', 'commit']:
        if len(argv) >= 3:
            kw['paths'] = argv[2:]
    
    # Determine arguments for propset/propget/etc commands
    if command == 'propset':
        if len(argv) < 5:
            log.error(usage)
            return ERROR
        else:
            kw['propname'] = argv[2]
            kw['propval'] = argv[3]
            kw['paths'] = argv[4:]
    elif command in ['propget', 'propdel']:
        if len(argv) < 4:
            log.error(usage)
            return ERROR
        else:
            kw['propname'] = argv[2]
            kw['paths'] = argv[3:]
    elif command == 'proplist':
        if len(argv) < 3:
            log.error(usage)
            return ERROR
        else:
            kw['paths'] = argv[2:]
    
    # Determine arguments for move and copy commands
    if command in ['copy', 'move']:
        if len(argv) != 4:
            log.error(usage)
            return ERROR
        else:
            kw['source'] = argv[2]
            kw['destination'] = argv[3]

    # Turn all paths (except 'directory') into relative paths
    directory = os.path.abspath(os.path.normpath(directory))
    if 'paths' in kw:
        relpaths = []
        for path in kw['paths']:
            abspath = os.path.abspath(os.path.normpath(path))
            relpath = abspath[len(directory):].lstrip(os.sep)
            relpaths.append(relpath)
        kw['paths'] = relpaths
    for k in ['source', 'destination']:
        if k in kw:
            abspath = os.path.abspath(os.path.normpath(kw[k]))
            relpath = abspath[len(directory):].lstrip(os.sep)
            kw[k] = relpath

    # Dispatch to command handler
    try:
        manager = RepositoryManager(directory)
        return manager.dispatch(command, **kw)
    except CheckpointError, e:
        log.error(e)
        return ERROR
