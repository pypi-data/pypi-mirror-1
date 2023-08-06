#!/usr/bin/env python
# encoding: utf-8

# MAGnet MAnifest Management - Readout and create lists of magnets in yaml format. 
# 
# Copyright © 2008 Arne Babenhauserheide
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>


"""MAGnet MAnifest Management - Readout and create lists of magnets in yaml format. 

Magma lists are lists of files which can be downloaded via magnet links. 

They are written in yaml format to be easily readable as well as flexible and powerful. 

!!! IN PLANNING PHASE !!!

This script parses the basic features of MAGMAv0.4, which is being specified at the moment. 
It doesn't parse the current MAGMAv0.2 files!

Use it only, if you want to take a peek at what the updated specification can bring. 

It depends on pyyaml: http://pyyaml.org/. 

The API documentation is available from http://gnuticles.gnufu.net/pymagma/, and the code is available from a Mercurial repository: http://freehg.org/u/ArneBab/magma/. 

Changes: 

0.3.3: 

- FIX: Import error - only imported from modules, not from installed ones.

0.3.2: 

- FIX: magma_list.py had wrong header line (tried to open with 'pythons').

0.3.1: 

- Added support for multiple substitude urls and altlocs. 

0.3.0: 

- Added ebuild_creator_cli.py as script. 

0.2.9: 

- Added (mostly fake) ebuild_creator_cli as proof of concept. 
- Changed "name" parameter in files to "filename" to avoid ambiguity (you remember, that this IS in planning phase). 

0.2.8: 

- FIX: Parsing failed, when passed invalid lists. 

0.2.7: 

- Added return values to all method and function docstrings. 

0.2.6: 

- Added docstrings to all functions and classes. 

0.2.5: 

- Added load and dump function to work with magma more easily: 
    - magma.load(filedata) returns a Magma object with all the attributes like magma.magnets, magma.files and magma.metadata . 
    - magma.dump(Magma object) returns its string presentation for saving in a file. 
- Name of the file list parameter and of the URN parameter can now be changed easily. 
- Some cleaning up. 

0.2.4: 

- FIX: Header missed the #

0.2.3: 

- FIX: Saved magma list missed the magma header. 

0.2.2: 

- magma_list.py magma_from_files TARGET file1, file2, ... now works. 

0.2.1: 

- names in the magma list no longer contain the path to the file. 
- Improved documentation. 

0.2: 

- Uses setuptools. 
- Adds Usage info. 
- magma_list.py now callable from commandline. 
- Documentation improvements and API docs. 
- Multiple file magma creation. 

0.1: 

- Creates and reads Magma lists. 

"""

from setuptools import setup, find_packages
from magma import __version__, __author__, __depends__

# Create the desription from the docstrings 

DESCRIPTION = __doc__.split("\n")[0]

LONG_DESCRIPTION = "\n".join(__doc__.split("\n")[1:])

DEPENDENCIES = __depends__.split(", ") # not yet used, because it is too extensive. 
# See install_requires in setup. 

setup(name='magma',
      version=__version__,
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION, 
      author=__author__,
      author_email='arne_bab@web.de',
      keywords=["magma", "yaml", "p2p", "magnet"], 
      license="GNU GPL-3 or later", 
      platforms=["any"], 
      install_requires = ["pyyaml"], 
      classifiers = [
            "License :: OSI Approved :: GNU General Public License (GPL)",
            "Programming Language :: Python",
            "Operating System :: OS Independent",
            "Topic :: Software Development :: Libraries :: Python Modules",
            "Topic :: Communications :: File Sharing", 
            "Topic :: Communications :: File Sharing :: Gnutella", 
            "Intended Audience :: Developers", 
            "Intended Audience :: End Users/Desktop", 
            "Environment :: Console", 
            "Development Status :: 1 - Planning", 
            #"Development Status :: 3 - Alpha"
            ],
      packages = find_packages('.'), 
      url='http://freehg.org/u/ArneBab/magma',
      py_modules=["magma" ],
      scripts=["magma/magma_list.py", "magma/magma_creator_cli.py"], 
     )
