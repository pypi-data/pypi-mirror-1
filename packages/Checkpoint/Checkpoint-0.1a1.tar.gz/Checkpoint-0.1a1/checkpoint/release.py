"""Release information"""

NAME = "Checkpoint"
VERSION = "0.1a1"
DESCRIPTION = "Checkpoint is a simple version-control-system"
LONG_DESCRIPTION = """
   Checkpoint watches all the files in a directory (recursively), and
   allows you to revert your directory to any point in the past that you
   did a 'commit' to save your changes.
   
   Checkpoint comes as both a command-line utility AND a programming API.

   Users will love the Checkpoint command-line utility for its simplicity, 
   and Developers will love to integrate Checkpoint into their Content 
   Management Systems and other software for easy file versioning support.

   Checkpoint creates a sub-directory called ".cpt" where it stores
   file revisions and other information.  Files are stored as regular
   flat files.  In the future, compression support may be added to Checkpoint
   to save on disk space.

   Checkpoint remembers files by their path and SHA-1 checksum, in order to 
   track file movement and avoid unnecessary duplicates in the 
   repository.
   """
AUTHOR = "Ian Charnas"
AUTHOR_EMAIL = "ian.charnas@gmail.com"
URL = "http://checkpoint.googlecode.com/"
DOWNLOAD_URL = "http://code.google.com/p/checkpoint/downloads/list"
