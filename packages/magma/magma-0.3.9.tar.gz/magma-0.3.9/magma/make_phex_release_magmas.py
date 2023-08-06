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

"""Create the magma lists for a Phex release via the commandline. 

Usage: create_phex_release_magma.py <windows-release-path> <osx-release-path> <gnu/linux-file-release-path> 

Examples: 
    - create_phex_release_magma.py phex_3.2.2.104.exe phex_3.2.2.104_osx.zip phex_3.2.2.104.zip

Plans: 
    - Use MAGMAv0.4
    - Do it less hackish: Use the magma module. 

Ideas: 
    - Get list of Sourceforge servers autmatically. 
"""

### Constants ###

SOURCEFORGE_MIRRORS = ["http://heanet.dl.sourceforge.net/sourceforge/", "http://internap.dl.sourceforge.net/sourceforge/", "http://mesh.dl.sourceforge.net/sourceforge/", "http://puzzle.dl.sourceforge.net/sourceforge/", "http://easynews.dl.sourceforge.net/sourceforge/", "http://osdn.dl.sourceforge.net/sourceforge/", "http://keihanna.dl.sourceforge.net/sourceforge/", "http://optusnet.dl.sourceforge.net/sourceforge/", "http://switch.dl.sourceforge.net/sourceforge/", "http://ovh.dl.sourceforge.net/sourceforge/", "http://kent.dl.sourceforge.net/sourceforge/", "http://osdn.dl.sourceforge.net/sourceforge/", "http://jaist.dl.sourceforge.net/sourceforge/", "http://ufpr.dl.sourceforge.net/sourceforge/", "http://umn.dl.sourceforge.net/sourceforge/", "http://nchc.dl.sourceforge.net/sourceforge/", "http://jaist.dl.sourceforge.net/sourceforge/"] #: A list of SF.net servers. The name of the project and the name of the file get appended at the end (MIRROR + project/ + filename). 

#: The footer line for the phex update magma list. 
PHEX_MAGMA_FOOTER = '''

# Phex: Copyright 2006 The Phex Team - GPL-2 or later.
# Link: http://phex.org
# Developer-link: http://sf.net/projects/phex

'''


def create_phex_magmas(files):
    """Create the magma files for all release types. """
    
    #: The different target platforms / release types in the same order as the filepath parameters. 
    RELEASE_TYPES = ["win", "osx", "other"]
    
    # Create a magma file for each release. 
    for i in range(len(RELEASE_TYPES)): 
        create_phex_magma(files[i], release_type = RELEASE_TYPES[i])
    

def create_phex_magma(path, release_type="win"):
    """Create a magma list for a single release_type"""
    # We need to create the sha1 hash in Gnutella style. 
    from magma.sha1_gnutella import sha1_gnutella
    sha1 = sha1_gnutella(path)
    
    # Also we need to strip the dirname. 
    from magma.create_simple_magma_list import strip_dirname
    filename = strip_dirname(path)
    
    # Now, after we got all necessary data, we simply write the respective magma file. 
    write_magma(sha1, filename, release_type)
    
    # Done :) 
    
    

def write_magma(sha1, filename, release_type="other"):
    """Create the magma file for a specific release type. 
    
    @param release_type: The target platform: win, osx or other
    @type release_type: String """
    
    # First get the data to write. 
    
    # First the header line. This won't change but it is different for each release type. 
    
    if release_type == "osx": 
        magma_data = """#MAGMAv0.2 magnet:?mt=.&as=http://dateien.draketo.de/phex_osx.magma&dn=phex_osx.magma"""
    elif release_type == "win": 
        magma_data = """#MAGMAv0.2 magnet:?mt=.&as=http://dateien.draketo.de/phex_win.magma&dn=phex_win.magma"""
    elif release_type == "other": 
        magma_data = """#MAGMAv0.2 magnet:?mt=.&as=http://dateien.draketo.de/phex_win.magma&dn=phex_win.magma"""
    else: 
        raise Exception("Unsupported release type. Supported types are osx, win, other")
    
    # Now the middle part between the magma header and the phex magnet. 
    
    magma_data += """

#This list contains the update URLs for Phex. 

list:
  
 - """
    
    # Now the magnet. We need the SHA1 and the filename. 
    
    SHA1 = sha1
    
    
    # The first line isn't completely generic. 
    magma_data += '''"magnet:?xt=urn:sha1:''' + SHA1 + '''
   &dn=''' + filename
   
    # The next sources are plain Phex clients with stable IPs or dyndns hostnames. 
   
    GNET_CLIENT_SOURCES = ["http://edrikor.dyndns.org:9846/uri-res/N2R?urn:sha1:"]
    for i in GNET_CLIENT_SOURCES: 
        magma_data += "&xs=" + i + SHA1
    
    # Now add the freebase cache. 
    
    magma_data += "&as=http://www.freebase.be/g2/dlcount.php?sha1=" + SHA1
     
    # Finally add Sourceforge mirrors. 
    
    for i in SOURCEFORGE_MIRRORS: 
        magma_data += "&as=" + i + "phex/" + filename
    
    # Now close the magnet link
    
    magma_data += '''"'''
    
    # And add filename information. 
    magma_data += '''
  file-name: ''' + filename
 
    # Now finish the file. 
    magma_data += PHEX_MAGMA_FOOTER
    
    # Now write the file. 
    if release_type == "osx": 
        write_to_file("phex_osx.magma", magma_data)
    elif release_type == "win": 
        write_to_file("phex_win.magma", magma_data)
    elif release_type == "other": 
        write_to_file("phex_other.magma", magma_data)
    else: 
        raise Exception("Unsupported release type. Supported types are osx, win, other")



def write_to_file(path, data):
    """Write the data to a file at the path."""
    f = open(path, "w")
    f.write(data)
    f.close()
    log("wrote " + path)
    

def log(data, log_type = "console"):
    """Log some data."""
    if log_type == "console": 
        print data

    

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
        create_phex_magmas(argv[1:])
