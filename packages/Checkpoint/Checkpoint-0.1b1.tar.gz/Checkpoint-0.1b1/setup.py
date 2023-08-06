#!python
"""Setuptools-based installation and packaging module"""

from __future__ import with_statement

# Ensure setuptools is available (download & install if necessary)
import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, find_packages

# Get package information (and googlecode_upload Command class)
import os
execfile(os.path.join("checkpoint", "release", "__init__.py"))

# Check to make sure required python is available
def check_python():
    if sys.version_info < (2,5):
        print "Python 2.5 or higher is required to run Checkpoint."
        sys.exit(1)

# Load long description from README file
readme = os.path.normpath(__file__ + "/../README")
with open(readme) as f:
    LONG_DESCRIPTION = f.read()

# Let setuptools work its magic!
setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    download_url=DOWNLOAD_URL,
	packages=find_packages(), # find python packages in this dir
	include_package_data=True, # include more than just the code
    # [distutils.commands]
    #     googlecode_upload = checkpoint.release:googlecode_upload
	cmdclass={'googlecode_upload': googlecode_upload},
	entry_points="""
	    [console_scripts]
	    checkpoint = checkpoint.command:main
	    cpt = checkpoint.command:main
	""",
	keywords=["checkpoint", "version control"],
	classifiers=[
	    "Development Status :: 3 - Alpha",
	    "Environment :: Console",
	    "Environment :: Plugins",
	    "Intended Audience :: Developers",
	    "Intended Audience :: End Users/Desktop",
	    "License :: OSI Approved :: BSD License",
	    "Operating System :: OS Independent",
	    "Programming Language :: Python",
	    "Topic :: Software Development :: Libraries :: Python Modules",
	    "Topic :: Software Development :: Version Control",
	    "Topic :: System :: Archiving",
	    "Topic :: Utilities"
	],
)


