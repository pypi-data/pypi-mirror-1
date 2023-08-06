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


"""Manage Magma lists. 

Magma lists are lists of files which can be downloaded via magnet links. 

They are written in yaml format to be easily readable as well as flexible and powerful. 

It depends on U{pyyaml <http://pyyaml.org/>}. 

An example magma file is I{example-0.4.magma}. 

This API documentation is avaible from U{http://gnuticles.gnufu.net/pymagma/}, and the code is avaible from a U{Mercurial repository <http://freehg.org/u/ArneBab/magma/>}. 

Usage of this module
====================

from magma import Magma

    >>> magma = Magma(magma_file="example-0.4.magma")

or 

    >>> magma = Magma(input_files=["input_file.txt", "input_file2.txt"])
    

API / usage
===========

B{Creating magma lists from input files}
    
Then create a list from input files. 
    >>> magma = Magma(input_files=["input_file.txt"])
    
And save the list. 
    >>> magma.save(path="example.magma")
    
Or output the list. 
    >>> print magma
    #MAGMAv0.4
    files:
    - hash:
        sha1: 3UJCLAOIZVCNAIT7TQYFLAP7ZNFW6G2G
      name: input_file.txt
    <BLANKLINE>
    
Or just return a list of its files. 
    >>> files = magma.files
    
or output all magnet links inside the magma list. 
   >>> magnets = magma.magnets
   >>> print magnets
   ['magnet:?xt=urn:sha1:3UJCLAOIZVCNAIT7TQYFLAP7ZNFW6G2G&dn=input_file.txt']
  
  
B{Reading from magma lists}
   
Then create the list. 
   >>> magma = Magma(magma_file="example.magma")
   
Now get the files
   >>> files = magma.files
   >>> for i in files: print i
   input_file.txt 3UJCLAOIZVCNAIT7TQYFLAP7ZNFW6G2G
   
Get the first file from the list. 
   >>> one_file = files[0]
   >>> print one_file
   input_file.txt 3UJCLAOIZVCNAIT7TQYFLAP7ZNFW6G2G
   
And output its magnet. 
   >>> file_magnet = one_file.magnet
   >>> print file_magnet
   magnet:?xt=urn:sha1:3UJCLAOIZVCNAIT7TQYFLAP7ZNFW6G2G&dn=input_file.txt
   
Or output all its (meta-) data. 
   >>> file_data = one_file.data
   >>> print file_data
   {'hash': {'sha1': '3UJCLAOIZVCNAIT7TQYFLAP7ZNFW6G2G'}, 'name': 'input_file.txt'}
   
Output all magnet links inside the magma list. 
   >>> magnets = magma.magnets
   >>> print magnets
   ['magnet:?xt=urn:sha1:3UJCLAOIZVCNAIT7TQYFLAP7ZNFW6G2G&dn=input_file.txt']
    
"""

from magma_list import Magma

#### Self-Test ####

def _test():
    """Do all doctests"""
    # Get the testmod function from the doctest module
    from doctest import testmod
    # And call it. 
    testmod()

# If this script gets called directly, do the doctests. 
if __name__ == "__main__": 
    _test()
