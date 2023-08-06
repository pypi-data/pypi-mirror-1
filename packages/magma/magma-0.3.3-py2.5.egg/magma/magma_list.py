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

try: # local install
	from create_simple_magma_list import FILE_LIST_NAME, URN_PARAMETER_NAME, MAGMA_0_4_HEADER, FILENAME_PARAMETER
except: # Installed version
	from magma.create_simple_magma_list import FILE_LIST_NAME, URN_PARAMETER_NAME, MAGMA_0_4_HEADER, FILENAME_PARAMETER


# We need yaml loading and dumping as main component. 
from yaml import load, dump

# Now we need the central magma class. This does most of the work. 

class Magma(object):
    """A Magma List."""
    def __init__(self, magma_file=None, input_files=None, creator=None, data=None, yaml_data=None, *args, **kwds):
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
        """Return a human readable representation of the yaml file.
        
        In effect return the yaml data with the magic header.
        
        @return: A human readable representation of the Magma file in yaml format (String)."""
        return "#MAGMAv0.4" + "\n" + self.get_yaml_data()
        
    def create_magma_from_files(self, file_paths): 
        """Create a magma file from given file paths. 
        
        @return: The Python dict for a Magma file - the magma data. 
        """
        try: 
            from create_simple_magma_list import Magma as SimpleMagma
        except: 
            from magma.create_simple_magma_list import Magma as SimpleMagma
        magma = SimpleMagma(file_paths)
        return magma.data
    
    def is_magma(self, yaml_data):
        """Check, if a given yaml data begins with the Magma header.
        
        @param yaml_data: Data in yaml format
        @type yaml_data: String
        @return: True or False
        """
        return yaml_data[:len(MAGMA_0_4_HEADER)] == MAGMA_0_4_HEADER
    
    def readout_yaml(self, yaml_data):
        """Readout a magma list from data in yaml format.
        
        @param yaml_data: Data in yaml format.
        @type yaml_data: String
        @return: The Python dict for a Magma file - the magma data. 
        """
        # First we now need to check, that this file is in MAGMAv0.4 format. 
        assert self.is_magma(yaml_data), "Doesn't begin with Magma v0.4 header " + MAGMA_0_4_HEADER
        # Now readout the data via yaml and return it. 
        data = load(yaml_data)
        # yaml returns None, if nothing is avaible. We need an empty dict though, if the Magma file was empty. 
        if data is None:
            data = {}
        return data
    
    def readout_magma_from_file(self, file_path):
        """Readout a magma list from the file_path
        
        @param file_path: The path to the magma file, either absolute or relative the the location this script is invoked from. 
        @type file_path: String
        @return: The Python dict for a Magma file - the magma data. """
        # First get the Magma file. This cries out, if the file doesn't exist. 
        file_handle = open(file_path, "r")
        # Read the data. 
        file_data = file_handle.read()
        # And close the file. 
        file_handle.close()
        # At the end, return the data. 
        return self.readout_yaml(file_data)
        
    def readout_files(self):
        """Get the files from the magma data
        
        @return: A list of all MagmaFile objects from the Magma.
        """
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
        """Get the magnet links of the files.
       
	# TODO: Include Alt-Locs. 

        @return: A list of all magnet links inside the Magma.
        """
        #: The list of magnets
        magnets = []
        # Add the magnet of each of the files. 
        for i in self.files: 
            magnets.append(i.magnet)
        return magnets
    
    def get_magma_metadata(self):
        """Get only the metadata, without the list of files.
        
        @return: A dict which contains only the metadata of the Magma without the files.
        """
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
        
	TODO: Clean out empty entries in the files and the metadata before saving. 
	self.data["gnutella"]["alt-locs"] = [] should disappear (if there are no other keys than alt-locs in gnutella, the gnutella dict should completely disappear, too). 

        @param path: The path to the target file.
        @type path: String
        @return: None
        """
        # First get the file handle for the magma file
        file_handle = open(path, "w")
        # Then write the data in yaml format. 
        file_handle.write(self.dump())
        # And close the file handle. 
        file_handle.close()
        
    def print_data(self):
        """Print the magma file in the yaml format.
        
        @return: A string representation of the Magma in yaml format.
        """
        # Then print the data
        print self.__str__()
        
    def get_yaml_data(self):
        """Return the yaml representation of the data.
        
        @return: The yaml representation of the data."""
        return dump(self.data, default_flow_style=False)
        
    def dump(self):
        """Return the yaml data. 
        
        @return: A string representation of the Magma in yaml format.
        """
        return "#MAGMAv0.4\n" + self.get_yaml_data()


# Also we have files inside the magma list. They hate a few extra attributes to be easier to use than raw dictionaries. 

class MagmaFile(object):
    """A file inside the magma list.
    
    Provides some abstractions for files inside Magma objects. 
    
        >>> magma_file = MagmaFile({FILENAME_PARAMETER: "input_file.txt", "urn": {"sha1": "3UJCLAOIZVCNAIT7TQYFLAP7ZNFW6G2G"}})
        >>> print magma_file.data
        {'urn': {'sha1': '3UJCLAOIZVCNAIT7TQYFLAP7ZNFW6G2G'}, 'Filename': 'input_file.txt'}
        >>> print magma_file.sha1_hash
        3UJCLAOIZVCNAIT7TQYFLAP7ZNFW6G2G
        >>> print magma_file.name
        input_file.txt
        >>> print magma_file.magnet
        magnet:?xt=urn:sha1:3UJCLAOIZVCNAIT7TQYFLAP7ZNFW6G2G&dn=input_file.txt

    
    """
    def __init__(self, data, *args, **kwds):
        """A file inside the magma list. 
        
        @param data: The data of this file. 
        @type data: Dict
        """
        #: All data of the file
        self.data = data
        #: The name of the file, so we can easily print it. Every MagmaFile needs a filename. 
        self.name = self.data[FILENAME_PARAMETER]
        #: The sha1 hash of the file. Every MagmaFile needs a sha1 hash. 
        self.sha1_hash = self.data[URN_PARAMETER_NAME]["sha1"]
        #: The list of alternate urls. 
        self.urls = self.readout_urls()
        #: The Other Gnutella clients who have the file. 
        self.Gnutella_alt_locs = self.readout_gnet_alt_locs()
        #: The magnet link of the file
        self.magnet = self.parse_magnet()
    
    def __str__(self): 
        """Show nicely readable information about the file.
        
        @return: Nicely readable information about the file (String). """
        return self.name + " " + self.sha1_hash

    def readout_urls(self):
        """Readout alternate urls from the data
        
        @return: A list of URLs which can be used as alternate fallback sources (which are unsafe, though, since it isn't sure that they will point to the same file when times change). """
        # If we have urls, return them. 
        if "urls" in self.data.keys(): 
            return self.data["urls"]
        # Else return an empty list. 
        else: 
            # First create the list, so adding new urls gets saved in the file. 
            self.data["urls"] = []
            # And return the empty list. 
            return self.data["urls"]


    def readout_gnet_alt_locs(self):
        """Readout the Alt-Locs from the data
        
        @return: A list of IPs with Port numbers which can be used together with the sha1 hash to construct alt-locs for Gnutella. """
        ALT_LOC_STRING = "alt-locs"
        # If we have alt-locs, return them. 
        if "gnutella" in self.data.keys() and ALT_LOC_STRING in self.data["gnutella"].keys(): 
            return self.data["gnutella"][ALT_LOC_STRING]
        # Else return an empty list. 
        else: 
            # First create the list, so adding new alt-locs gets saved in the file. 
            if not "gnutella" in self.data.keys(): 
                self.data["gnutella"] = {}
            self.data["gnutella"][ALT_LOC_STRING] = []
            # And return the empty list. 
            return self.data["gnutella"][ALT_LOC_STRING]
        
    
    def parse_magnet(self): 
        """Parse the magnet link from the data inside the file.
        
        @return: A magnet link for the file (String). """
        # From this we create the xt. 
        xt = "urn:sha1:" + self.sha1_hash
        # And from it we get dn
        dn = self.name
        params = {"xt": xt, "dn": dn}
        # Now get the urlencode method
        from urllib import urlencode
        #: The magnet link is a String. 
        magnet = "magnet:?" + urlencode(params)
        # TODO: Include alt-locs. 
        return magnet


def usage(): 
    """Usage instructions.
    
    @return: Usage instructions (String)."""
    # Just use the docstring. 
    usage = __doc__.split("\n\n")[1:]
    usage_string = "\n\n".join(usage)
    return usage_string
    
def _test(): 
    """Do all doctests.
    
    @return: None"""
    from doctest import testmod
    testmod()

# If this gets called automatically, load the magma list and print the magnets, or create a magma list. 
if __name__ == "__main__": 
    # _test()
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
