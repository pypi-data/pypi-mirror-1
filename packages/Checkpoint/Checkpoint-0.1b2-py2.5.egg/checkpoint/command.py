""""""
import os 
import sys
import logging
from textwrap import dedent

from checkpoint.error import *
from checkpoint.manager import CheckpointManager
from checkpoint.release import DESCRIPTION, VERSION, URL

__all__ = []

log = logging.getLogger("checkpoint")

SUCCESS = 0
ERROR = 1

def main(argv=sys.argv):
    usage = """
        usage:  %(prog)s <subcommand> [options] [args]
        Checkpoint command-line utility, version %(version)s

        Most subcommands accept a directory argument.  If this argument is not
        specified, the current directory will be used by default.

        Available subcommands:
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

    # Determine Checkpoint command
    try:
        command = argv[1]
        if command not in CheckpointManager.COMMANDS:
            raise ValueError
    except (IndexError, ValueError):
        print usage
        return ERROR

    # Determine command options
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option('-c', dest="changeset", default=None, type='int')
    try:
        (options, extra_args) = parser.parse_args(argv[2:])
    except:
        print usage
        return ERROR

    # Determine Checkpoint directory (default to current directory)
    if len(extra_args) > 0:
        directory = extra_args[0]
    else:
        directory = os.getcwd()

    # If 'recover' was requested, confirm this with the user
    if command == 'recover':
        print dedent("""
            --------------------------------------------------------------
            !!! Confirm Crash Recovery! !!!
    
            You have selected crash recovery.  This process will move all
            files to a new crash recovery directory in the repository, 
            and then one-by-one restore your files from the good copies
            in the repository.
        
            If this process is interrupted for any reason, you can try 
            recovery again to attempt to restore your files.  If recovery
            still does not finish successfully, or if it finishes successfully
            but you still appear to be missing files, you may have to try 
            manual crash-recovery.  See the documentation for more details.
            --------------------------------------------------------------
        
        """)
        
        choice = raw_input("Proceed with crash recovery [yes/no]: ")
        if choice.lower() != "yes":
            print "Crash recovery was cancelled."
            return SUCCESS

    # Dispatch to command handler
    try:
        manager = CheckpointManager(directory)
        return manager.dispatch(command, options)
    except CheckpointError, e:
        print >> sys.stderr, "%s\n" % e.message
        return ERROR
