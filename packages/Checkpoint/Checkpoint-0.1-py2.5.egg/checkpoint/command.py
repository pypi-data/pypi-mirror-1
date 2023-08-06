"""Checkpoint command-line utility (CLI)"""

import os 
import sys
import logging
from textwrap import dedent
from optparse import OptionParser

from checkpoint.manager import MirrorManager, RepositoryManager
from checkpoint.release import DESCRIPTION, VERSION, URL
from checkpoint.error import CheckpointError

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

def mirror(argv=sys.argv):
    usage = """
        usage:  %(prog)s <command> [args]
        Checkpoint Mirror command-line utility, version %(version)s

        Most commands accept a directory argument.  If this argument is not
        specified, the current directory will be used by default.
        
        Mirror Commands:
            mirror <source-dir> <dest-dir>  Mirror a checkpoint directory
            refresh [<dir>]                 Bring a mirror up to date
            forget [<dir>]                  Delete mirror configuration
            recover [<dir>]                 Recover after a crash or failure
    
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
        print usage
        return ERROR
    
    # Determine command arguments
    source_directory = None
    destination_directory = None
    
    if command == 'mirror':
        # For 'mirror', determine the source and destination directories.
        if len(argv) == 3:
            source_directory = argv[2]
            destination_directory = os.getcwd()
        elif len(argv) == 4:
            source_directory = argv[2]
            destination_directory = argv[3]
        else:
            print usage
            return ERROR
    elif command in ['refresh', 'forget', 'recover']:
        # Determine the mirror dir (default to current dir).
        if len(argv) == 3:
            destination_directory = argv[2]
        else:
            destination_directory = os.getcwd()
    else:
        print usage
        return ERROR

    # If 'recover' was requested, confirm this with the user
    if command == 'recover':
        print crash_recovery_confirmation
        choice = raw_input("Proceed with crash recovery [yes/no]: ")
        if choice.lower() != "yes":
            print "Crash recovery was cancelled."
            return SUCCESS

    # Dispatch to command handler
    try:
        manager = MirrorManager(destination_directory=destination_directory)
        if command == 'mirror':
            kw = dict(source_directory=source_directory)
        else:
            kw = dict()
        return manager.dispatch(command, **kw)
    except CheckpointError, e:
        print >> sys.stderr, "%s\n" % e.message
        return ERROR
        
def repository(argv=sys.argv):
    usage = """
        usage:  %(prog)s <command> [options] [args]
        Checkpoint command-line utility, version %(version)s

        Most commands accept a directory argument.  If this argument is not
        specified, the current directory will be used by default.

        Repository Commands:
            watch [<dir>]                   Watch directory for changes
            status [<dir>]                  List all changes since last commit
            commit [<dir>]                  Save all changes since last commit
            revert -c changeset [<dir>]     Revert to a previous changeset
            forget [<dir>]                  Delete saved history of changes
            recover [<dir>]                 Recover after a crash or failure
    
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
        print usage
        return ERROR

    # Determine command options
    parser = OptionParser()
    parser.add_option('-c', dest="changeset", default=None, type='int')
    try:
        (options, extra_args) = parser.parse_args(argv[2:])
    except:
        print usage
        return ERROR

    # Determine the Checkpoint dir (default to current dir).
    if len(extra_args) == 1:
        directory = extra_args[0]
    else:
        directory = os.getcwd()

    # If 'recover' was requested, confirm this with the user
    if command == 'recover':
        print crash_recovery_confirmation
        choice = raw_input("Proceed with crash recovery [yes/no]: ")
        if choice.lower() != "yes":
            print "Crash recovery was cancelled."
            return SUCCESS

    # Dispatch to command handler
    try:
        manager = RepositoryManager(directory)
        if command == 'revert':
            kw = dict(desired_changeset=options.changeset)
        else:
            kw = dict()
        return manager.dispatch(command, **kw)
    except CheckpointError, e:
        print >> sys.stderr, "%s\n" % e.message
        return ERROR
