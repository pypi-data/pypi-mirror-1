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


A simple Magma file looks like the following:: 
    #MAGMAv0.4
    files:
    - filename: input_file.txt
      urn:
        sha1: 3UJCLAOIZVCNAIT7TQYFLAP7ZNFW6G2G
    - filename: input_file2.txt
      urn:
        sha1: 3UJCLAOIZVCNAIT7TQYFLAP7ZNFW6G2G


This script parses the basic features of MAGMAv0.4, which is being specified at the moment. 
It doesn't parse the current MAGMAv0.2 files!

Use it only, if you want to take a peek at what the updated specification will bring. 


It depends on U{pyyaml <http://pyyaml.org/>}, tagpy and IPy. 

An example magma file is I{example-0.4.magma}. 

This API documentation is avaible from U{http://gnuticles.gnufu.net/pymagma/}, and the code is avaible from a U{Mercurial repository <http://freehg.org/u/ArneBab/magma/>}. 

The module can also be found in the U{Python Package Index (PyPI) <http://pypi.python.org/pypi/magma/>}. It is available under the GPL-3 or later. 

It is being written by U{Arne Babenhauserheide <http://draketo.de>}. If you wish to contribute, please drop me a mail with the word "tunnel" somewhere in the subject line (to get past my spamfilter). My email: arne_bab at web de . 

Usage of this module
====================

    >>> # from magma import *
    >>> magma = open_file("example-0.4.magma")

or 

    >>> magma = create_from_input_files(["input_file.txt", "input_file2.txt"])


API / usage
===========

B{Creating magma lists from input files}
    
Create a list from input files. 
    >>> magma = create_from_input_files(["input_file.txt"])
    
Output the list, showing the empty entries, which could be filled with data. 
    >>> print magma
    #MAGMAv0.4
    files:
    - filename: input_file.txt
      gnutella:
        alt-locs: []
      urls: []
      urn:
        sha1: 3UJCLAOIZVCNAIT7TQYFLAP7ZNFW6G2G
    <BLANKLINE>
    # Magmav0.2 compatibility section
    list:
     - "magnet:?xt=urn%3Asha1%3A3UJCLAOIZVCNAIT7TQYFLAP7ZNFW6G2G&dn=input_file.txt"
    <BLANKLINE>
    
And save it to a file with the empty entries cleaned away. 
    >>> magma.save(path="example.magma")


Or just return a list of its files as MagmaFiles. 
    >>> files = magma.files
    
Or output all magnet links inside the magma list. 
   >>> print magma.magnets
   ['magnet:?xt=urn%3Asha1%3A3UJCLAOIZVCNAIT7TQYFLAP7ZNFW6G2G&dn=input_file.txt']
  
  
B{Reading from magma lists}
   
Readout the data from a file. 
   >>> magma = open_file("example.magma")
   
Now get the files inside the list. 
   >>> files = magma.files
   >>> for i in files: print i
   input_file.txt 3UJCLAOIZVCNAIT7TQYFLAP7ZNFW6G2G
   
Get the first file from the list. 
   >>> one_file = files[0]
   >>> print one_file
   input_file.txt 3UJCLAOIZVCNAIT7TQYFLAP7ZNFW6G2G
   
And output its magnet. 
   >>> print one_file.magnet
   magnet:?xt=urn%3Asha1%3A3UJCLAOIZVCNAIT7TQYFLAP7ZNFW6G2G&dn=input_file.txt
   
Or output all its (meta-) data. 
   >>> print one_file.data
   {'urn': {'sha1': '3UJCLAOIZVCNAIT7TQYFLAP7ZNFW6G2G'}, 'gnutella': {'alt-locs': []}, 'urls': [], 'filename': 'input_file.txt'}
   

Output all magnet links inside the magma list. 
   >>> print magma.magnets
   ['magnet:?xt=urn%3Asha1%3A3UJCLAOIZVCNAIT7TQYFLAP7ZNFW6G2G&dn=input_file.txt']

Load a Magma object from a string containing Magma data via magma.load(). 
As test, load a minimal Magma file, containing nothing but the header.
   >>> magma = load("#MAGMAv0.4")
   
And cry out, if the string doesn't begin with the Magma header (isn't Magma data!). 
   >>> magma = load("a:b")
   Traceback (most recent call last):
   ...
   AssertionError: Doesn't begin with Magma v0.4 header #MAGMAv0.4

Also dump yaml data via magma.dump()
   >>> print dump(magma)
   #MAGMAv0.4
   {}
   <BLANKLINE>
   # Magmav0.2 compatibility section
   list:
   <BLANKLINE>

Or just print the Magma data. 
   >>> print magma
   #MAGMAv0.4
   {}
   <BLANKLINE>
   # Magmav0.2 compatibility section
   list:
   <BLANKLINE>


Plans: Gnutella
    - Also pass metadata and include that alongside the file list. 
    - Add Alt-locs (depends on the network used). Maybe GNet-Alt-Loc for Gnutella. Gets parsed to magnet xs automatically. 
   
Ideas: 
    - Readout metadata from files, for example using the taglib, pyPdf or such. 
    - If given both magma list and files, the magma list gets extended by the files. 
    - Joining and seperating magma lists. 
    - Passing several additional input lists to join with the main list. 
    - Passing the data of files along with magma metadata to create the list. 
    - Passing the indizes of files to automatically slice the list. maybe even with the syntax sliced_magma = magma[a:b]
    - If a dir gets passed, add all files within that dir. Alsa a parameter to ask, if it should be done recursively. 
    - If hashing files takes very long (for example seen with clock.tick()), give more output. 
    - Add more commandline switches (verbose, help, ... - see the babtools_gentoo script)

"""

#### Background ####

__author__ = 'Arne Babenhauserheide'
__copyright__ = 'Copyright (C) 2008 Arne Babenhauserheide'
__date__ = '2008-05-09'
__licence__ = 'GPL-3 or later'
__program__ = 'MAGnet MAnifest Management'
__version__ = '0.3.8'

# The dependencies of the _init__ only. 
__depends__ = ''

def parse_dependencies(init_depends):
    """Aggregate the dependencies from all submodules.
    
    @param init_depends: The dependencies of the __init__ file. 
    @type init_depends: String 
    @return: A string with dependencies, seperated by ', '. 
    """
    # aggregate dependencies from all submodules. 
    dep_list = [init_depends]
    from create_simple_magma_list import __depends__ 
    dep_list.append(__depends__)
    from magma_list import __depends__
    dep_list.append(__depends__)
    from sha1_gnutella import __depends__
    dep_list.append(__depends__)
    
    # Now aggregate it, simply using a set, which discards multiple entries. 
    deps = set()
    for i in dep_list: 
        # We need to turn the individual __depends__ into lists to add them. 
        [deps.add(j) for j in i.split(", ")]
    # And discard a possibly included emtpy string (if there is no "", nothing happens). 
    deps.discard("")
    
    # Now assign it as string to the __depends__
    return ", ".join(deps)

__depends__ = parse_dependencies(__depends__)


#### Background ####

#### Constants ####

#### Constants ####


from magma_list import Magma

def open_file(filepath):
    """Open a file as Magma list and produce the corresponding Python object.
    
    @param filepath: The path to a Magma file.
    @type filepath: String
    @return: A Magma Object. 
    """
    return Magma(magma_file=filepath)

def create_from_input_files(files):
    """Create a magma file from given input files.
    
    @param files: A list of file paths
    @type files: List of Strings
    @return: A Magma Object."""
    return Magma(input_files=files)

def load(yaml_data):
    """Parse a Magma list and produce the corresponding Python object.
    
    @param yaml_data: Data read from a yaml file
    @type yaml_data: String
    @return: A Magma Object. 
    """
    return Magma(yaml_data=yaml_data)
    
def dump(magma):
    """Return the string representation of the Magma file.
    
    @param magma: A Magma object.
    @type magma: magma.Magma
    @return: A String represenation of the Magma file (in yaml format). 
    """
    return magma.__str__()
    
    


#### Self-Test ####

def _test():
    """Do all doctests.
    
    @return: None
    """
    # Get the testmod function from the doctest module. 
    from doctest import testmod
    # And call it. 
    testmod()

# If this script gets called directly, do the doctests. 
if __name__ == "__main__": 
    _test()
