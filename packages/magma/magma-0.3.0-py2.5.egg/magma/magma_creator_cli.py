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

It is mainly a proof of concept, yet. 

Ideas: 
    - Check, if tagpy or similar are avaible, and if yes, add metadata from the file tags. 
"""

# Import basic Magma classes. 
from magma_list import Magma
from magma_list import MagmaFile 


def ask_audio(files, magma): 
    """Ask, whether one of the files is a audio file."""
    print "Now, let's make it a audio list."
    print ""
    audio = raw_input("Is one of the file a audio file (yes/No)? ")
    # Ask until the user 
    while not audio.lower() in ["yes", "no", "", "y", "n"]: 
        audio = raw_input("Is one of the file a audio file? Please answer either 'yes' or 'no'. Just clicking enter skips: ")
    # If we have no audio files, we return instantly. 
    if audio.lower() == "no" or audio.lower() == "n" or audio.lower() == "": 
        return 
    
    # Else, the answer was yes, and we can go on. 
    # First get the file which is a audio file. TODO: Add support for multiple mutimedia files. 
    
    audio = raw_input("Please enter which file it is (1 or 2 or ...): ")
    while not audio in [str(i) for i in range(1, len(magma.files) + 1)]: 
        audio = raw_input("Please enter a valid number (1 or 2 or ...): ")
    print "Now onwards to editing file", audio + ":", magma.files[int(audio) -1].name
    file_to_edit = magma.files[int(audio) -1]
    file_to_edit.path = files[int(audio) -1]
    edit_file(file_to_edit)
    
    print "So now, the file looks like this:"
    
    print magma
    
    magma_filename = raw_input("Please enter a name to which to save the file. it should end on .magma: ")
    magma.save(magma_filename)
    
    print "Magma file saved as", magma_filename
    
    print "It contains the following magnets:"
    for i in magma.magnets: 
        print i


def edit_file(magma_file):
    """Edit the data inside a magma file - add metadata."""
    # First check, which metadata we can get automatically. 
    print "First this script will try to get some values automatically. "
    automatically_generated_tags = []
    # Create the media subdict
    magma_file.data["audio"] = {}
    try: 
        from tagpy import FileRef
        # The basic object from tagpy. 
        filetags = FileRef(magma_file.path)
        # The object with audiodata. 
        audioprops = filetags.audioProperties()
        tagfile = filetags.file()
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
    except: 
        pass
    
    print "The following tags were added:"
    for i in automatically_generated_tags: 
        print i
    # TODO: Ask the user which of the tags to add. 
    
    magma_file.data["title"] = raw_input("Please enter the title of the file: ")
    magma_file.data["description"] = raw_input("Please enter a description of the file: ")
    
    # Now add one of the artists. 
    magma_file.data["artists"]  = []
    artist1 = {}
    artist1["name"] = raw_input("Please enter the name of its artist: ")
    artist1["website"] = raw_input("Please enter an url to the website of the artist: ")
    magma_file.data["artists"] .append(artist1)
    
    # And add some more data. 
    magma_file.data["audio"]["album"] = raw_input("Please enter the name of the album: ")
    magma_file.data["year"] = raw_input("Please enter the year when this work was published: ")
    magma_file.data["audio"]["tracknumber"] = raw_input("Please enter the tracknumber of this file: ")
    



def create_magma_list_interactively(files):
    """Create magma files interactively via commandline dialogs.
    
    @param files: A list of files to hash.
    @type files: List
    """
    magma = Magma(input_files=files)
    print "Basic magma list: "
    print magma
    
    ask_audio(files, magma)
    
    


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
    create_magma_list_interactively(argv[1:])
