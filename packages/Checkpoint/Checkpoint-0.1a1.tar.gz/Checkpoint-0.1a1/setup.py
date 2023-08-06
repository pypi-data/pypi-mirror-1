#!/usr/bin/env python

# Ensure setuptools is available (download & install if necessary)
import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, find_packages

# Get package information from release.py
import os
execfile(os.path.join("checkpoint", "release.py"))

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
	zip_safe=True,
	entry_points="""
	    [console_scripts]
	    checkpoint = checkpoint.checkpoint:main
	    cpt = checkpoint.checkpoint:main
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
