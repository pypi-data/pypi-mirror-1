#!/usr/bin/env python

"""Setup for Screencast Writer

Copyright 2006 Baiju M <baiju.m.mail@gmail.com>

This program is released under GNU GPL version 2,
or (at your option) any later version

$Id$
"""

import os

from setuptools import setup, Extension, find_packages
    
setup(
    name='screencastwriter',
    description='Screencast Writer is screencast helper tool',
    version='0.1',
    author='Baiju M',
    author_email='baiju.m.mail@gmail.com',
    url='http://zissue.berlios.de/tools/scw/',
    download_url='http://zissue.berlios.de/tools/scw-0.1.0.tar.bz2',
    license='GPL v2',
    
    zip_safe=False,
    data_files=[
    ('screencastwriter', ['src/screencastwriter/scw.glade']),
    ('screencastwriter', ['README.txt']),
    ('screencastwriter', ['src/screencastwriter/testcast.txt']),
    ],
    scripts = ['src/scw'],
    package_dir = {"screencastwriter": "src/screencastwriter"},
    packages = ["screencastwriter"],
    classifiers = [
    "Programming Language :: Python",
    "License :: OSI Approved :: GNU General Public License (GPL)",
    "Natural Language :: English",
    "Development Status :: 3 - Alpha",
    "Operating System :: POSIX",
    "Environment :: X11 Applications",
    "Intended Audience :: Developers",
    "Topic :: Desktop Environment",
    "Topic :: Software Development",
    ],
)
