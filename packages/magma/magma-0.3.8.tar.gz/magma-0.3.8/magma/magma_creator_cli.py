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

"""Create magma files interactively via commandline dialogs.

Usage: magma_creator_cli.py file1 file2, ...

Examples: 
    - magma_creator_cli.py input_file.txt input_file2.txt Infinite-Hands--free-software.ogg 


This will implement features from magma-for-streaming-mediav0.07.txt

It is mainly a proof of concept, yet, and it may change! 

Ideas: 
    - Check, if tagpy or similar are avaible, and if yes, add metadata from the file tags. 
"""

# Import basic Magma classes. 
from magma_list import Magma
from magma_list import MagmaFile 


def edit_file(magma_file):
    """Edit the data inside a magma file - add metadata."""
    # First check, which metadata we can get automatically. 
    print "First this script will try to get some values automatically. "
    automatically_generated_tags = []
    
    if not magma_file.name.endswith(".mp3") or magma_file.name.endswith(".ogg"): 
        print "No mp3 or ogg file. We only support mp3 and ogg vorbis at the moment."
        return 
    
    # Create the audio subdict
    magma_file.data["audio"] = {}
    try: 
        from tagpy import FileRef
        # The basic object from tagpy. 
        filetags = FileRef(magma_file.path)
        print "yes, FileRef"
        # The object with audiodata. 
        try: 
            audioprops = filetags.audioProperties()
        except: pass
        try: 
            tagfile = filetags.file()
        except: pass
        try: 
            tag = filetags.tag()
        except: pass
        
        try: 
            # The length of time this file plays. 
            magma_file.data["audio"]["length-ms"] = audioprops.length*1000
            automatically_generated_tags.append(("length-ms", magma_file.data["audio"]["length-ms"]))
        except: pass
        try: 
            # The bitrate of the file. 
            magma_file.data["audio"]["bitrate-kbps"] = audioprops.bitrate
            automatically_generated_tags.append(("bitrate-kbps", magma_file.data["audio"]["bitrate-kbps"]))
        except: pass
        try: 
            # The sampling rate. 
            magma_file.data["audio"]["samplerate-Hz"] = audioprops.sampleRate
            automatically_generated_tags.append(("samplerate-Hz", magma_file.data["audio"]["samplerate-Hz"]))
        except: pass
        try: 
            # And the raw filesize. 
            magma_file.data["size-Bytes"] = tagfile.length()
            automatically_generated_tags.append(("size-Bytes", magma_file.data["size-bits"]))
        except: pass
        
        # Now to the general metatags of the file content. 
        try: 
            # The title of the file
            magma_file.data["audio"]["title"] = tag.title
            automatically_generated_tags.append(("title", magma_file.data["audio"]["title"]))
        except: pass
        
        try: 
            # The publish year of the file
            magma_file.data["audio"]["year"] = tag.year
            automatically_generated_tags.append(("year", magma_file.data["audio"]["year"]))
        except: pass
        
        try: 
            # The track number of the file
            magma_file.data["audio"]["track"] = tag.track
            automatically_generated_tags.append(("track", magma_file.data["audio"]["track"]))
        except: pass
        
        try: 
            # The genre of the file
            magma_file.data["audio"]["genre"] = tag.genre
            automatically_generated_tags.append(("genre", magma_file.data["audio"]["genre"]))
        except: pass
        
        try: 
            # The comment of the file
            magma_file.data["audio"]["comment"] = tag.comment
            automatically_generated_tags.append(("comment", magma_file.data["audio"]["comment"]))
        except: pass
    except: pass
    
    print "The following tags were added:"
    for i in automatically_generated_tags: 
        print i
    
    



def create_magma_list_interactively(files):
    """Create magma files interactively via commandline dialogs.
    
    @param files: A list of files to hash.
    @type files: List
    """
    magma = Magma(input_files=files)
    print "Basic magma list: "
    print magma
    
    print "------ ------ ------ ------ ------ ------ "

    print "Now we try add metadata using tagpy. "
    for i in range(len(magma.files)): 
        magma.files[i].path = files[i]
        edit_file(magma.files[i])
    
    print "------ ------ ------ ------ ------ ------ "
    print "The magma list now looks like this: "
    print "---"
    print magma
    
    ip_port = raw_input("... \nIf you use Gnutella, you can now give a list of IP:PORT pairs seperated by spaces as alternate-locations. For example you can give your clients IP and its port, alternately your dyndns host and your client port. They can greatly increase the performance of downloads but break your anonymity. \nExample: 127.0.0.1:6465 0.0.0.0:9999 example.dyndns.org:1234 \nIf you want to add alt-locs, please add the IP:PORT pairs now: ")
    alt_locs = ip_port.split()
    
    try: 
        #from IPy import IP
        #for i in alt_locs: 
        #    ip = IP(i.split(":")[0])
    
        if len(alt_locs) > 0: 
            for i in magma.files: 
                i.data["gnutella"]["alt-locs"] = alt_locs
    except: 
        print "You need the IPy module to add alt-locs, and the IP addresses need to be valid. No alt-locs added."
        print "To fix it just run 'easy_install IPy', and check the format of the IPs"
    
    target_file = raw_input("Where shall we save it? ")
    magma.save(target_file)
    
    

def usage(): 
    """Usage instructions.
    
    @return: Usage instructions (String)."""
    # Just use the docstring. 
    usage = __doc__.split("\n\n")[1:]
    usage_string = "\n\n".join(usage)
    return usage_string

#### Self-Test ####

def _test(): 
    """Do all doctests.
    
    @return: None"""
    from doctest import testmod
    testmod()

# If this gets called automatically, load the magma list and print the magnets, or create a magma list. 
if __name__ == "__main__": 
    _test()
    from sys import argv
    if argv[1] in ["--help", "-h", "?", "--usage"]: 
        print usage()
    else: 
        create_magma_list_interactively(argv[1:])
