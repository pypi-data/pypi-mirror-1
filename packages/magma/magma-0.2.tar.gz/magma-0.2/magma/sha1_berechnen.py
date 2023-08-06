#!/usr/bin/env python
# encoding: utf-8
"""Readout a file and calculate the sha1-hash. Output it base32 encoded. """ 

#### Background ####

__author__ = 'Arne Babenhauserheide <arne_bab ät web punkt de>'
__copyright__ = 'Copyright (C) 2007 Arne Babenhauserheide'
__date__ = '2007-07-06'
__licence__ = 'GPL-2 or later'
__program__ = 'sha1 aus Datei berechnen'
__version__ = '0.1'
__depends__ = 'hashlib, base64'

#### Background ####

#### Imports ####

# We need the sha1-hashing function from haslib
from hashlib import sha1

# and for encoding the hash we need the base32 encoding function from base64
from base64 import b32encode

#### Imports ####

def sha1_berechnen(filename): 
    """Calculate the sha1-hash and output it base32 encoded as it is required by magnetlinks. Takes the filename as input"""
    # First we create 
    #: The file-object
    try: 
        file = open(filename, "r")
    except: 
        print "Error when reading file"
        return Null
    # Then we get 
    #: A line of data readout from the file. 
    dataline = file.readline()
    # so we can calculate arbitrary large files without running out of memory (as long as the lines aren't too long). # TODO: don't calculate by line, but by a fixed amount of bytes. 
    
    # Next we call in
    #: The sha1-function
    sha = sha1()
    
    # into which we can then route the data, line by line
    # while the dataline isn't empty (\n aka linebreak is not empty)
    # We put the datalines into sha1. 
    while dataline != "": 
        sha.update(dataline)
	# And get the next dataline
	dataline = file.readline()
    
    # Via digest, this function can then output
    # the sha1 hash as bytes. 
    # we put it through bb32encode() to generate
    #: The base32 encoded sha1-hash
    xt_sha1 = b32encode(sha.digest())
    
    # At last return the base32 encoded sha1 hash of the file. 
    return xt_sha1

#### User-Input ####

# This sample input just calculates the sha1-hash of the script itself. 

filename = "sha1_berechnen.py" 
# filename = raw_input("Dateiname und Pfad eingeben: ")

#### User-Input ####

#### Self-Test ####

# If the script is called directly 
# and given a commandline argument, 
# parse that file. 

if __name__ == "__main__": 
    from sys import argv
    if len(argv) < 2: 
        print sha1_berechnen(filename)
    else: 
        print sha1_berechnen(argv[1])

### Self-Test ####
