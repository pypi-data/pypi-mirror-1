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


"""Sha1 Gnutella - Readout files and calculate the sha1-hashes. Output them base32 encoded. 

Usage: 
 - sha1_gnutella.py <file1> <file2> ... 


Output: 
<sha1-hash1> <filename1>
<sha1-hash2> <filename2>
""" 

#### Background ####

__depends__ = 'hashlib, base64'

#### Background ####

#### Imports ####

# We need the sha1-hashing function from haslib
from hashlib import sha1

# and for encoding the hash we need the base32 encoding function from base64
from base64 import b32encode

from os.path import isfile

#### Imports ####

#### Constants ####

#: The length of the segments to read in one go. 
FILE_FRAGMENT_SIZE_BYTES =  10 * 1024 * 1024 # 10 MiB, because it doesn't really make a difference, but like this, the disk might be able to do something else for a moment, if the files are bigger than 10MiB, and smaller files get accessed only once. 

#### Constants ####


def sha1_gnutella(filepath, fragment_size = FILE_FRAGMENT_SIZE_BYTES): 
    """Calculate the sha1 hash and output it base32 encoded as is required by magnet links. 
    
    @param filepath: The path to the file to hash. Must be a file! This function is too low level to add recursion into subdirectories. 
    @type filepath: String
    
    @param fragment_size: Length of the fragment to read in bytes.
    @type fragment_size: Int
    
    @return: The sha1 hash, base32 encoded (String). 
    """
    
    # As really first part, we check, if the path leads to a file. If it doesn't we just return. 
    if not isfile(filepath): 
        raise Exception("Error when reading file. Does the path exist? " + filepath)
    
    # First we create 
    #: The file-object
    try: 
        file = open(filepath, "r")
    except: 
        print "Error when reading file. Does the path exist?", filepath
        raise Exception("Error when reading file. Does the path exist? " + filepath)
    # Then we get 
    #: A line of data readout from the file. 
    fragment = file.read(fragment_size)
    
    # so we can calculate arbitrary large files without running out of memory. 
    
    # Next we call in
    #: The sha1-function
    sha = sha1()
    
    # Into which we can then route the data. 
    
    # If the fragment is smaller than the fragment_size, 
    if len(fragment) < fragment_size and False: 
        # we can close the file instantly 
        # and then get the sha1. 
        # This way we get rid uf uselessly open files at once. 
        file.close()
        sha.update(fragment)
    else: 
        # while the fragment isn't empty
        # We put the fragments into sha1. 
        
        # We first update once
        sha.update(fragment)
        
        # And then only update as long as the length of the fragment is equal to the fragment size. 
        # If we'd test, if it's empty, we'd need one useless read. 
        while len(fragment) == fragment_size: 
            # Get the next fragment
            fragment = file.read(fragment_size)
            # And update the sha1
            sha.update(fragment)
        file.close()
    # Via digest, this function can then output
    # the sha1 hash as bytes. 
    # we put it through bb32encode() to generate
    #: The base32 encoded sha1-hash
    xt_sha1 = b32encode(sha.digest())
    
    # At last return the base32 encoded sha1 hash of the file. 
    return xt_sha1

#### User-Input ####

# This sample input just calculates the sha1-hash of the script itself. 

filepath = "sha1_gnutella.py" 
# filepath = raw_input("Dateiname und Pfad eingeben: ")

#### User-Input ####

#### Self-Test ####

def test_speed(files, min=1024 * 1024, max=15*1024*1024, step=1024 * 1024):
    """Test different settings of the fragment_size. 
    
    Result: The fragment_size is almost irrelevant. Anything between 512kiB and 10MiB offers about the same speed.
    
    @param files: The files to hash.
    @type files: List
    @return: None
    """
    from time import time
    start_time = 0
    stop_time = 0
    for i in range(min, max, step): 
        start_time = time()
        for j in files: 
            try: 
                sha1_gnutella(j, i)
            except: pass
        stop_time = time()
        print "Segment_Size (MiB):", i / 1024.0 / 1024.0, "time:", stop_time - start_time

def help(): 
    """Display the usage information."""
    print __doc__

# If the script is called directly 
# and given a commandline argument, 
# parse that file. 

if __name__ == "__main__": 
    from sys import argv
    if len(argv) < 2 or argv[1] in ["-h", "--help", "?"]: 
        help()

    else: 
        # Calculate a sha1 for all given files.
        for i in argv[1:]: 
            try: 
                print sha1_gnutella(i), i
            except: pass

### Self-Test ####
