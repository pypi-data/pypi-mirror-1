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


"""
Returns a magma-list containing the file name. Takes the names as input.

# Test strip_dirname

    >>> a = "blah/blubb/bangala/goi.gis"
    >>> print strip_dirname(a)
    goi.gis
    
    >>> a = "/blah/blubb/bangala/goi.gis"
    >>> print strip_dirname(a)
    goi.gis
    
"""
# Get the sha1_berechnen module. 
from sha1_berechnen import sha1_berechnen
# And get the yaml dumper and loader
from yaml import dump, load
# And the dirname to be able to strip it. 
from os.path import dirname

def strip_dirname(path):
    """Strip everything but the name of the file."""
    # We just as many characters from the beginning of the string as the dirname is long. 
    if len(dirname(path)) > 0: 
        filename = path[len(dirname(path)) + 1:]
    else: 
        filename = path
    return filename

class Magma: 
    def __init__(self, inputfilenames): 
        self.filenames = inputfilenames
        self.sha1 = {}
        for i in self.filenames: 
            self.sha1[i] = sha1_berechnen(i)
        self.magma = self.magma()
        self.data = load(self.magma)
        
    def magma(self): 
        magma = {}
        list_of_magnets = []
        for i in self.filenames: 
            magnet = {}
            magnet['hash'] = {}
            magnet['hash']['sha1'] = self.sha1[i]
            magnet['name'] = strip_dirname(i)
            list_of_magnets.append(magnet)
        magma['files'] = list_of_magnets
        return "#MAGMAv0.4\n" + dump(magma, default_flow_style=False)

def _test(): 
    from doctest import testmod
    testmod()

#### Self-Test ####
if __name__ == '__main__': 
    from sys import argv
    if len(argv) > 1: 
        filenames = argv[1:]
    else: 
        # filename = "magma_liste_erzeugen.py"
        filenames = [raw_input("Dateiname und Pfad eingeben: ")]
        gnutella_client_ip = raw_input("Eigene IP oder dyndns-Adresse eingeben: ")
    magma = Magma(filenames)
    print magma.magma
    
    # And test. 
    _test()
    
