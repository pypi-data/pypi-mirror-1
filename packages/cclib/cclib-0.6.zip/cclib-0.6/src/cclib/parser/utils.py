"""
cclib (http://cclib.sf.net) is (c) 2006, the cclib development team
and licensed under the LGPL (http://www.gnu.org/copyleft/lgpl.html).
"""

__revision__ = "$Revision: 361 $"

import adfparser
import gamessparser
import gaussianparser
import gamessukparser
import molproparser
import logging

def ccopen(filename,progress=None,loglevel=logging.INFO,logname="Log"):
    """Guess the identity of a particular log file and return an instance of it.
    
    Returns: one of ADF, GAMESS, GAMESS UK, Gaussian, or
             None (if it cannot figure it out).
    """
    filetype = None
    inputfile = open(filename, "r")
    for line in inputfile:
        if line.find("Amsterdam Density Functional") >= 0:
            filetype = adfparser.ADF
            break
        elif line.find("GAMESS") >= 0:
            filetype = gamessparser.GAMESS
            # don't break as it may be a GAMESS-UK file
        elif line.find("G A M E S S - U K") >= 0:
            filetype = gamessukparser.GAMESSUK
            break
        elif line.find("Gaussian, Inc.") >= 0:
            filetype = gaussianparser.Gaussian
            break
        elif line.find("PROGRAM SYSTEM MOLPRO") >= 0:
            filetype = molproparser.Molpro
            break
    inputfile.close() # Need to close before creating an instance
    
    if filetype: # Create an instance of the chosen class
        filetype = apply(filetype, [filename,progress,loglevel])
        
    return filetype

def convertor(value, fromunits, tounits):
    """Convert from one set of units to another.

    >>> print "%.1f" % convertor(8, "eV", "cm-1")
    64524.8
    """
    _convertor = {"eV_to_cm-1": lambda x: x*8065.6,
                  "hartree_to_eV": lambda x: x*27.2114,
                  "bohr_to_Angstrom": lambda x: x*0.529177,
                  "nm_to_cm-1": lambda x: 1e7/x,
                  "cm-1_to_nm": lambda x: 1e7/x,
                  "hartree_to_cm-1": lambda x: x*219474.6}

    return _convertor["%s_to_%s" % (fromunits, tounits)] (value)

class PeriodicTable(object):
    """Allows conversion between element name and atomic no.

    >>> t = PeriodicTable()
    >>> t.element[6]
    'C'
    >>> t.number['C']
    6
    >>> t.element[44]
    'Ru'
    >>> t.number['Au']
    79
    """
    def __init__(self):
        self.element = [None,
            'H', 'He',
            'Li', 'Be',
            'B', 'C', 'N', 'O', 'F', 'Ne',
            'Na', 'Mg',
            'Al', 'Si', 'P', 'S', 'Cl', 'Ar',
            'K', 'Ca',
            'Sc', 'Ti', 'V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn',
            'Ga', 'Ge', 'As', 'Se', 'Br', 'Kr',
            'Rb', 'Sr',
            'Y', 'Zr', 'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd', 'Ag', 'Cd',
            'In', 'Sn', 'Sb', 'Te', 'I', 'Xe',
            'Cs', 'Ba',
            'La', 'Ce', 'Pr', 'Nd', 'Pm', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho', 'Er', 'Tm', 'Yb',
            'Lu', 'Hf', 'Ta', 'W', 'Re', 'Os', 'Ir', 'Pt', 'Au', 'Hg',
            'Tl', 'Pb', 'Bi', 'Po', 'At', 'Rn',
            'Fr', 'Ra',
            'Ac', 'Th', 'Pa', 'U', 'Np', 'Pu', 'Am', 'Cm', 'Bk', 'Cf', 'Es', 'Fm', 'Md', 'No',
            'Lr', 'Rf', 'Db', 'Sg', 'Bh', 'Hs', 'Mt', 'Ds', 'Rg', 'Uub']
        self.number = {}
        for i in range(1, len(self.element)):
            self.number[self.element[i]] = i

if __name__ == "__main__":
    import doctest, utils
    doctest.testmod(utils, verbose=False)
