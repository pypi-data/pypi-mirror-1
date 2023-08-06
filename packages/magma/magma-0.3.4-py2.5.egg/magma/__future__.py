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


"""Features which should be available in the future, but aren't yet well tested. 

New Features will first be implemented here and moved to the main part of the module as soon as they are ready (to give you a bit of shielding from the mistakes we're bound to make). 

You shouldn't count on features from __feature__ to come into the present whatever happens. Some might just have been the wrong approach, and others might prove too bugprone or similar. 

"""

all_feature_names = []

# Import the classes we want to improve. 
try: 
    from magma import Magma as CurrentMagma
except: 
    from magma_list import Magma as CurrentMagma
try: 
    from magma.magma_list import MagmaFile as CurrentMagmaFile
except: 
    from magma_list import MagmaFile as CurrentMagmaFile


# First subclass Magma, and initialize it. 
# It is the main class, and most functionality should go here. 
class Magma(CurrentMagma):
    def __init__(self, *args, **kwds):
        super(Magma, self).__init__(*args, **kwds)

# Then also subclass MagmaFile, and initialize it. 
class MagmaFile(CurrentMagmaFile):
    def __init__(self, *args, **kwds):
        super(MagmaFile, self).__init__(*args, **kwds)
