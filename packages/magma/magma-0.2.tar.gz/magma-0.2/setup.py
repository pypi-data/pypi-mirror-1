#!/usr/bin/env python
# encoding: utf-8

#    magma - Readout and create Magma lists. 
# 
#    Copyright © 2008 Arne Babenhauserheide
# 
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>


"""Readout and create Magma lists. 

Magma lists are lists of files which can be downloaded via magnet links. 

They are written in yaml format to be easily readable as well as flexible and powerful. 

It depends on pyyaml: http://pyyaml.org/. 

This API documentation is avaible from http://gnuticles.gnufu.net/pymagma/, and the code is avaible from a Mercurial repository: http://freehg.org/u/ArneBab/magma/. """

from setuptools import setup, find_packages

# Create the desription from the docstrings 

DESCRIPTION = __doc__.split("\n")[0]

LONG_DESCRIPTION = "\n".join(__doc__.split("\n")[1:])

setup(name='magma',
      version='0.2',
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION, 
      author='Arne Babenhauserheide',
      author_email='arne_bab@web.de',
      keywords=["magma", "yaml", "p2p", "magnet"], 
      license="GNU GPL-3 or later", 
      platforms=["any"], 
      install_requires = ["pyyaml"], 
      packages = find_packages('.'), 
      url='http://freehg.org/u/ArneBab/magma',
      py_modules=["magma" ],
      scripts=["magma/magma_list.py"]
     )
