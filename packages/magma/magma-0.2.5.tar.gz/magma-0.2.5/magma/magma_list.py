#!/usr/bin/env pythons
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


"""Tools for reading out magma lists. 

Usage: magma_list.py CMD [OPT]

Commands: 
    - magnets_from_magma MAGMA_FILE
    - magma_from_files MAGMA FILE1 FILE2 ... 

Examples: 
    - magma_list.py magnets_from_magma example-0.4.magma
    - magma_list.py magma_from_files example-0.4.magma blah.txt foo.txt gam.txt
"""

__depends__ = "yaml"

from create_simple_magma_list import FILE_LIST_NAME, URN_PARAMETER_NAME, MAGMA_0_4_HEADER


# We need yaml loading and dumping as main component. 
from yaml import load, dump

# Now we need the central magma class. This does most of the work. 

class Magma(object):
    """A Magma List."""
    def __init__(self, magma_file=None, input_files=None, creator=None, data=None, yaml_data=None):
        """A Magma list. 
        
        @param magma_file: The path to the magma file, either absolute or relative the the location this script is invoked from. 
        @type magma_file: String
        
        @param input_files: A list of file_paths of input files which should be included in the magma list. 
        @type input_files: List
        
        @param creator: An identifier for the creator of the Magma file. 
        @type creator: String
        
        @param data: Raw file data as read from a Magma file. 
        @type data: String
        
        """
        #: All data inside the Magma list
        self.data = None
        # if we get data, we assign it. 
        if data is not None: 
            self.data = data
        # If we get data in yaml format (String), we read it out. 
        elif yaml_data is not None: 
            self.data = self.readout_yaml(yaml_data)
        # If we get a magma file, we readout the file itself. 
        elif magma_file is not None: 
            self.data = self.readout_magma_from_file(magma_file)
        # If we get single files, we create the magma file from the files. 
        elif input_files is not None: 
            self.data = self.create_magma_from_files(file_paths=input_files)
        else: 
            raise Exception("No input specified. Youl need to pass one of data=DATA, magma_file=PATH or input_files=[PATH1, PATH2, ...]")
            
        # If we get a creator name, also add that. 
        if creator is not None: 
            self.data["creator"] = creator
        
        #: All files inside the Magma list. 
        self.files = self.readout_files()
        
        #: All magnets inside the Magma list. 
        self.magnets = self.get_file_magnets()
        
        #: The metadata of this Magma list (excluding the files). 
        self.metadata = self.get_magma_metadata()
        
    def __str__(self): 
        """Return a human readable representation of the yaml file almost the same as print.
        
        In effect return the yaml data with the magic header."""
        return "#MAGMAv0.4" + "\n" + self.get_yaml_data()
        
    def create_magma_from_files(self, file_paths): 
        """Create a magma file from given file paths"""
        try: 
            from create_simple_magma_list import Magma as SimpleMagma
        except: 
            from magma.create_simple_magma_list import Magma as SimpleMagma
        magma = SimpleMagma(file_paths)
        return magma.data
    
    def readout_yaml(self, yaml_data):
        """Readout a magma list from data in yaml format.
        
        @param yaml_data: Data in yaml format.
        @type yaml_data: String
        """
        # First we now need to check, that this file is in MAGMAv0.4 format. 
        assert yaml_data[:len(MAGMA_0_4_HEADER)] == MAGMA_0_4_HEADER, "Doesn't begin with Magma v0.4 header " + MAGMA_0_4_HEADER
        # Now readout the data via yaml and return it. 
        data = load(yaml_data)
        # yaml returns None, if nothing is avaible. We need an empty dict though, if the Magma file was empty. 
        if data is None: 
            data = {}
        return data
    
    def readout_magma_from_file(self, file_path):
        """Readout a magma list from the file_path
        
        @param file_path: The path to the magma file, either absolute or relative the the location this script is invoked from. 
        @type file_path: String"""
        # First get the Magma file. This cries out, if the file doesn't exist. 
        file_handle = open(file_path, "r")
        # Read the data. 
        file_data = file_handle.read()
        # And close the file. 
        file_handle.close()
        # At the end, return the data. 
        return self.readout_yaml(file_data)
        
    def readout_files(self):
        """Get the files from the magma data"""
        # The files are held as simple list inside the magma file. 
        #: The list of files inside the Magma list. 
        file_list = []
        
        # If the Magma list contains files, we read them. 
        if FILE_LIST_NAME in self.data.keys(): 
            # We turn every file dict inside the magma list into a MagmaFile object and return them. 
            for i in self.data[FILE_LIST_NAME]: 
                file_list.append(MagmaFile(i))
        # Now the only thing left is returning the list. 
        return file_list
        
    def get_file_magnets(self): 
        """Get the magnet links of the files."""
        #: The list of magnets
        magnets = []
        # Add the magnet of each of the files. 
        for i in self.files: 
            magnets.append(i.magnet)
        return magnets
    
    def get_magma_metadata(self):
        """Get only the metadata, without the list of files."""
        # First we need an empty dictionary to hold the metadata (we want to carve out the files key, so we just add all other keys). 
        magma_metadata = {}
        # Now we add all subdictionaries, except the "files" subdict. 
        for i in self.data: 
            if i != FILE_LIST_NAME: 
                magma_metadata[i] = self.data[i]
        # That's it. 
        return magma_metadata
        
    def save(self, path):
        """Save the magma list to the path. 
        
        If the folder to save in doesn't exist, just raise an Exception.
        
        @param path: The path to the target file.
        @type path: String"""
        # First get the file handle for the magma file
        file_handle = open(path, "w")
        # Then write the data in yaml format. 
        file_handle.write(self.dump())
        # And close the file handle. 
        file_handle.close()
        
    def print_data(self):
        """Print the magma file in the yaml format."""
        # Then print the data
        print self.__str__()
        
    def get_yaml_data(self):
        """Return the yaml representation of the data."""
        return dump(self.data, default_flow_style=False)
        
    def dump(self):
        """Return the yaml data"""
        return "#MAGMAv0.4\n" + self.get_yaml_data()


# Also we have files inside the magma list. They hate a few extra attributes to be easier to use than raw dictionaries. 

class MagmaFile(object):
    """A file inside the magma list"""
    def __init__(self, data):
        """A file inside the magma list"""
        #: All data of the file
        self.data = data
        #: The name of the file, so we can easily print it. 
        self.name = self.data["name"]
        #: The sha1 hash of the file. 
        self.sha1_hash = self.data[URN_PARAMETER_NAME]["sha1"]
        #: The magnet link of the file
        self.magnet = self.parse_magnet()
    
    def __str__(self): 
        """Show nicely readable information about the file."""
        return self.name + " " + self.sha1_hash
    
    def parse_magnet(self): 
        """Parse the magnet link from the data inside the file."""
        # From this we crate the xt. 
        xt = "urn:sha1:" + self.sha1_hash
        # And from it we get dn
        dn = self.name
        #: The magnet link is a String. 
        magnet = "magnet:?xt=" + xt + "&dn=" + dn
        # TODO: Include alt-locs. 
        return magnet


def usage(): 
    """Print usage instructions."""
    # Just use the docstring. 
    usage = __doc__.split("\n\n")[1:]
    usage_string = "\n\n".join(usage)
    return usage_string

# If this gets called automatically, load the magma list and print the magnets, or create a magma list. 
if __name__ == "__main__": 
    from sys import argv
    if len(argv) < 3: 
        print usage()
    elif argv[1] == "magnets_from_magma": 
        magma = Magma(magma_file=argv[2])
        for i in magma.magnets: 
            print i
    elif argv[1] == "magma_from_files": 
        magma = Magma(input_files=argv[3:])
        magma.save(argv[2])
    else: 
        print usage()
