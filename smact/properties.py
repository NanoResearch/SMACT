###############################################################################
# Copyright Haonan Le, Daniel Davies, Adam J. Jackson, Keith T. Butler (2016) #
#                                                                             #
# This file is part of SMACT: properties.py is free software: you can         #
# redistribute it and/or modify it under the terms of the GNU General Public  #
# License as published by the Free Software Foundation, either version 3 of   #
# the License, or (at your option) any later version.  This program is        #
# distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;   #
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A       #
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.   #
# You should have received a copy of the GNU General Public License along     #
# with this program.  If not, see <http://www.gnu.org/licenses/>.             #
#                                                                             #
###############################################################################

import smact
from numpy import sqrt, product, exp, mean
from smact.data import get_mulliken
from smact.data import get_pauling


def band_gap_Harrison(verbose=False, anion=None, cation=None,
                      distance=None, elements_dict=None):

    """
    Estimates the band gap from elemental data.

    The band gap is estimated using the principles outlined in
    Harrison's 1980 work "Electronic Structure and the Properties of
    Solids: The Physics of the Chemical Bond".

    Args:
        Anion (str): Element symbol of the dominant anion in the system.

        Cation (str): Element symbol of the the dominant cation in the system.
        Distance (float or str): Nuclear separation between anion and cation
                i.e. sum of ionic radii.
        verbose: An optional True/False flag. If True, additional information
                is printed to the standard output. [Defult: False]
        elements_dict (dict): Element symbol keys with smact.Element
                objects values. This may be provided to prevent
                excessive reading of data files.

    Returns (float): Band gap in eV.

    """

    # Set constants
    hbarsq_over_m = 7.62

    # Get anion and cation
    if anion:
        An = anion
    if cation:
        Cat = cation
    if not anion:
        An = raw_input("Enter Anion Symbol:")
    if not cation:
        Cat = raw_input("Enter Cation Symbol:")
    if distance:
        d = float(distance)
    if not distance:
        d = float(raw_input("Enter internuclear separation (Angstroms): "))

    # Get elemental data:
    if not elements_dict:
        elements_dict = smact.element_dictionary((An, Cat))
    An, Cat = elements_dict[An], elements_dict[Cat]

    # Calculate values of equation components
    V1_Cat = (Cat.eig - Cat.eig_s)/4
    V1_An = (An.eig - An.eig_s)/4
    V1_bar = (V1_An + V1_Cat)/2
    V2 = 2.16 * hbarsq_over_m / (d**2)
    V3 = (Cat.eig - An.eig)/2
    alpha_m = (1.11*V1_bar)/sqrt(V2**2 + V3**2)

    # Calculate Band gap [(3-43) Harrison 1980 ]
    Band_gap = (3.60/3)*(sqrt(V2**2 + V3**2))*(1-alpha_m)
    if verbose:
        print "V1_bar = ", V1_bar
        print "V2 = ", V2
        print "alpha_m = ", alpha_m
        print "V3 = ", V3

    return Band_gap


def compound_electroneg(verbose=False, elements=None, stoichs=None,
                        elements_dict=None, source='Mulliken'):

    """Estimate electronegativity of compound from elemental data.

    Uses Mulliken electronegativity by default, which uses elemental
    ionisation potentials and electron affinities. Alternatively, can
    use Pauling electronegativity, re-scaled by factor 2.86 to achieve
    same scale as Mulliken method (Nethercot, 1974)
    DOI:10.1103/PhysRevLett.33.1088 .

    Geometric mean is used (n-th root of product of components), e.g.:

    X_Cu2S = (X_Cu * X_Cu * C_S)^(1/3)

    Args:
    elements: A list of elements given as standard elemental symbols.
    Optional: if not used, interactive input of space separated
    elemental symbols will be offered.
    stoichs: A list of stoichiometries, given as integers or floats.
    Optional: if not used, interactive input of space separated
    integers  will be offered.
    verbose: An optional True/False flag. If True, additional information
    is printed to the standard output. [Default: False]
    elements_dict: Dictionary of smact.Element objects; can be provided to
    prevent multiple reads of data files
    source: String 'Mulliken' or 'Pauling'; type of Electronegativity to
    use. Note that in SMACT, Pauling electronegativities are
    rescaled to a Mulliken-like scale.

    Returns:
    Electronegativity: Estimated electronegativity as a float.
    Electronegativity is a dimensionless property.

    Raises:
    (There are no special error messages for this function.)
    """

    if elements:
        elementlist = elements
    if stoichs:
        stoichslist = stoichs

    # Get elements and stoichiometries if not provided as argument
    if not elements:
        elementlist = list(raw_input(
            "Enter elements (space separated): ").split(" "))
    if not stoichs:
        stoichslist = list(raw_input(
            "Enter stoichiometries (space separated): ").split(" "))

    if not elements_dict:
        elements_dict = smact.element_dictionary(elements)

    # Convert stoichslist from string to float
    stoichslist = map(float, stoichslist)

    # Get electronegativity values for each element
    if source == 'Mulliken':
        elementlist = [get_mulliken(elements_dict[el])
                       for el in elementlist]
    elif source == 'Pauling':
        elementlist = [2.86 * get_pauling(elements_dict[el])
                       for el in elementlist]
    else:
        raise Exception("Electronegativity type '{0}'".format(source),
                        "is not recognised")
    # Print optional list of element electronegativities.
    # This may be a useful sanity check in case of a suspicious result.
    if verbose:
        print "Electronegativities of elements=", elementlist

    # Raise each electronegativity to its appropriate power
    # to account for stoichiometry.
    for i in range(0, len(elementlist)):
        elementlist[i] = [elementlist[i]**stoichslist[i]]

    # Calculate geometric mean (n-th root of product)
    prod = product(elementlist)
    compelectroneg = (prod)**(1.0/(sum(stoichslist)))

    if verbose:
        print "Geometric mean = Compound 'electronegativity'=", compelectroneg

    return compelectroneg


def compound_electroneg_pauling(verbose=False, elements=None,
                                stoichs=None, elements_dict=None):

    """
    Estimate Mulliken electronegativity of compound from elemental data

    The estimate is based on Pauling electronegativities. A scaling
    factor of 2.86 is applied; his brings the electronegativities to a
    Mulliken-like scale, allowing or estimation of Fermi level.

    Geometric mean is used (n-th root of product of components), e.g.:

    X_Cu2S = (X_Cu * X_Cu * C_S)^(1/3)

    Args:
        elements: A list of elements given as standard elemental symbols.
        Optional: if not used, interactive input of space separated
        elemental symbols will be offered.
        stoichs: A list of stoichiometries, given as integers or floats.
        Optional: if not used, interactive input of space separated
        integers  will be offered.
        verbose: An optional True/False flag. If True, additional information
               is printed to the standard output. [Default: False]
        elements_dict: Dictionary of smact.Element objects; can be provided to
               prevent multiple reads of data files

    Returns:
        Electronegativity: Estimated electronegativity as a float.
                         Electronegativity is a dimensionless property.

    Raises:
        (There are no special error messages for this function.)

    """
    return compound_electroneg(verbose=verbose, elements=elements,
                               stoichs=stoichs,
                               elements_dict=elements_dict,
                               source='Pauling')

def SSE_min_gap(Compound,SSE_2015=True):
    '''
    A function to calculate the minimum of the SSE band gap.
    Args:
        Compound : a list of smact Species.
        SSE_2015 : Boolean - should I use SSE1 or SSE_2015 values.
    Returns:
        gap : real number, the calculated minimum SSE band gap in eV.
    '''
    anions = []
    cations = []
    for ele in Compound:
        if ele.oxidation < 0:
            if SSE_2015:
                anions.append(ele.SSE_2015)
            else:
                anions.append(ele.SSE)
        else:
            if SSE_2015:
                cations.append(ele.SSE_2015)
            else:
                cations.append(ele.SSE)
    gap = min(cations) - max(anions)
    return gap

def SSE_average_gap(Compound,SSE_2015=True):
    '''
    A function to calculate the average SSE band gap.
    Args:
        Compound : a list of smact Species.
        SSE_2015 : Boolean - should I use SSE1 or SSE_2015 values.
    Returns:
    Returns:
        gap : real number, the calculated average SSE band gap in eV.
    '''
    anions = []
    cations = []
    for ele in Compound:
        if ele.oxidation < 0:
            if SSE_2015:
                anions.append(ele.SSE_2015)
            else:
                anions.append(ele.SSE)
        else:
            if SSE_2015:
                cations.append(ele.SSE_2015)
            else:
                cations.append(ele.SSE)
    gap = mean(cations) - mean(anions)
    return gap

def SSE_weight_gap(Compound,x,SSE_2015=True):
    '''
    A function to calculate the weighted average of the SSE band gap.
    Args:
        Compound : a list of smact Species.
        SSE_2015 : Boolean - should I use SSE1 or SSE_2015 values.
    Returns:
        x : real number, the weighting factor
    Returns:
        gap : real number, the calculated SSE band gap in eV.
    '''
    anions = []
    cations = []
    for ele in Compound:
        if ele.oxidation < 0:
            if SSE_2015:
                anions.append(ele.SSE_2015)
            else:
                anions.append(ele.SSE)
        else:
            if SSE_2015:
                cations.append(ele.SSE_2015)
            else:
                cations.append(ele.SSE)
    if max(cations) == min(cations):
        F1 = 0.5
    else:
        F1 = 0.5 * exp(-1 * (max(cations) - min(cations))**-x)
    if max(anions) == min(anions):
        F2 = 0.5
    else:
        F2 = 0.5 * exp(-1 * (max(anions) - min(anions))**-x)

    gap = F1 * max(cations) + (1-F1) * min(cations) - (1-F2) * max(anions) - F2 * min(anions)
    return gap
