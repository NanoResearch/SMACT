#!/usr/bin/env python 
import numpy as np

class Lattice(object):
      """A class of objects to hold the structure stoiciometry"""

      def __init__(self, sites, site_ratios, site_oxidations):
	self.sites = sites
	self.site_ratios = site_ratios
	self.site_oxidations = site_oxidations
#------------------------------------------------------------------------------------
def check_lattice_charges(charges, site_elements, sites):
# Check if all sub-lattice charges sum to zero, append to list if true
	if np.sum(charges) == 0:
# Need to use two lists, new contains the present composition; site_elements is the 
# list of all news found.
	    site_elements.append(sites)

        return site_elements
#------------------------------------------------------------------------------------
def possible_compositions(crystal, elements):
    """Seach for the elements which satisfy the possible oxidations and chrge neutrality"""
    """As input it takes the crystal class and the dictionary elements, which contains the oxidation state data for the elements"""
# Initialise the array atom, containing possible elements for each sub lattice
    atom = []
# Initialise the array, site_elements, containing compositions found
    site_elements = []
    i = 0
    while i < len(crystal.sites):
        atom.append(possible_elements(elements, crystal.site_oxidations[i]))
        i = i + 1

# I could not think of an elegant way to generalise this. For now it loops through the possible
# lattices until it reaches the number, then it goes no further. Therefore, many of the loops
# here are redundant. 
# site_n refers to the possible element @ site n
# we multiply these by oxidation number to get sub-lattice charge
    i = 0
    for site_1 in atom[0]:
        charges = np.zeros(shape=(len(atom)))
        charges[0] = int(elements[site_1]) * crystal.site_ratios[0]
	if len(atom) == 1:
	    sites = [site_1]
	    site_elements = check_lattice_charges(charges, site_elements, sites)
	if 2 <= len(atom):       #Are ther more sites to check?
      	    for site_2 in atom[1]:
                charges[1] = int(elements[site_2]) * crystal.site_ratios[1]
		if len(atom) == 2:    #If we have sampled all sites test the charge
	            sites = [site_1, site_2]
		    site_elements = check_lattice_charges(charges, site_elements, sites)
	        if 3 <= len(atom):    #Are ther more sites to check?
                    for site_3 in atom[2]:
                        charges[2] = int(elements[site_3]) * crystal.site_ratios[2]
	                if len(atom) == 3: #If we have sampled all sites test the charge
	                    sites = [site_1, site_2, site_3]
		            site_elements = check_lattice_charges(charges, site_elements, sites)
		        if 4 <= len(atom): #Are ther more sites to check?
                            for site_4 in atom[3]:
                                charges[3] = int(elements[site_4]) * crystal.site_ratios[3]
	                        if len(atom) == 4: 
	                            sites = [site_1, site_2, site_3, site_4]
		                    site_elements = check_lattice_charges(charges, site_elements, sites)
			    if 5 <= len(atom):
			    	for site_5 in atom[4]:
				    charges[4] = int(elements[site_5]) * crystal_site_ratios[4] 
	                            if len(atom) == 5:
	                                sites = [site_1, site_2, site_3, site_4]
		                        site_elements = check_lattice_charges(charges, site_elements, sites)

    return site_elements
#------------------------------------------------------------------------------------
def possible_elements(elements, oxidations):
    """Possible atoms to occupy a site"""
    atoms = []
    for element in elements:
        for ox_state_a in oxidations:
        	if int(elements[element]) == int(ox_state_a):
        	    atoms.append(element)
    return atoms
#------------------------------------------------------------------------------------


