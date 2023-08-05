#!/usr/bin/env python

from distutils.core import setup

"""Setup script for pexif"""

setup (
    name = "pexif",
    version = "0.2",
    description = "A module for editing JPEG EXIF data",
    long_description = "This module allows you to parse and edit the EXIF data tags in a JPEG image.",
    author = "Ben Leslie",
    author_email = "benno@benno.id.au",
    url = "http://www.benno.id.au/code/pexif/",
    license = "python",
    py_modules = ["pexif"],
    scripts = ["scripts/dump_exif.py"],
    platforms = ["any"],
    classifiers = ["Development Status :: 3 - Alpha",
                   "Intended Audience :: Developers",
                   "Operating System :: OS Independent",
                   "Programming Language :: Python",
                   "License :: OSI Approved :: Python Software Foundation License",
                   "Topic :: Multimedia :: Graphics"]
    )
    
    
