#!/usr/bin/env python 
# Using the ase spacegroup module this can build the structure, from 
# the composition, as defined in the smact_lattice module. 
#TODO:
# Estimate the cell parameters based on radii from tables.
# Add further types, Spinnel, Flourite, Delafossite ....
################################################################################
# Copyright Keith T Butler    (2013)                                           #
#                                                                              #
# This file is part of SMACT: builder.py is free software: you can             #
# redistribute it and/or modify it under the terms of the GNU General Public   #
# License as published by the Free Software Foundation, either version 3 of    #
# the License, or (at your option) any later version.                          #
# This program is distributed in the hope that it will be useful, but WITHOUT  #
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or        #
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for    #
# more details.                                                                #
# You should have received a copy of the GNU General Public License along with #
# this program.  If not, see <http://www.gnu.org/licenses/>.                   #
#                                                                              #
################################################################################

from ase.lattice.spacegroup import crystal


def cubic_perovskite(species,cell_par=[6,6,6,90,90,90],repetitions=[1,1,1]):
	 system = crystal((species), 
	 basis=[(0,0,0), (0.5, 0.5, 0.5), (0.5, 0.5, 0)],
         spacegroup=221, size = repetitions, cellpar=cell_par)
	
         return system

def spinel(species,cell_par=[8,8,8,90,90,90],repetitions=[1,1,1]):
	 system = crystal((species),
	 basis=[(0.0, 0.0, 0.0),(0.625, 0.625, 0.625),(0.3873, 0.3873, 0.3873)],
	 spacegroup=227,size=repetitions,cellpar=cell_par)

         return system

def wurtzite(species, cell_par=[2,2,6,90,90,120],repetitions=[1,1,1]):
         system = crystal((species),
         basis=[(2./3.,1./3.,0),(2./3.,1./3.,5./8.)],
         spacegroup=186, size = repetitions, cellpar=[3, 3, 6, 90,90,120])

         return system