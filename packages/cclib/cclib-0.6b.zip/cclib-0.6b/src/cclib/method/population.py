"""
cclib (http://cclib.sf.net) is (c) 2006, the cclib development team
and licensed under the LGPL (http://www.gnu.org/copyleft/lgpl.html).
"""

__revision__ = "$Revision: 238 $"

import Numeric
import logging

from calculationmethod import Method

class Population(Method):
    """A base class for all population-type methods"""
    def __init__(self, parser, progress=None, \
                 loglevel=logging.INFO, logname="Log"):

        # Call the __init__ method of the superclass
        super(Population, self).__init__(parser, progress, loglevel, logname)
        self.fragresults = None
        
    def __str__(self):
        """Return a string representation of the object."""
        return "Population"

    def __repr__(self):
        """Return a representation of the object."""
        return "Population"
    

#create array for mulliken charges
        self.logger.info("Creating atomcharges: array[1]")
        size = len(self.atomresults[0][0])
        self.atomcharges = Numeric.zeros([size], "f")
        
        for spin in range(len(self.atomresults)):

            for i in range(self.parser.homos[spin]+1):

                temp = Numeric.reshape(self.atomresults[spin][i], (size,))
                self.atomcharges = Numeric.add(self.atomcharges, temp)
        
        if not unrestricted:
            self.atomcharges = Numeric.multiply(self.atomcharges, 2)

        return True

    def partition(self, indices=None):

        if not hasattr(self, "aoresults"):
            self.calculate()

        if not indices:
#build list of groups of orbitals in each atom for atomresults
            if hasattr(self.parser, "aonames"):
                names = self.parser.aonames
            elif hasattr(self.parser, "fonames"):
                names = self.parser.fonames

            atoms = []
            indices = []

            name = names[0].split('_')[0]
            atoms.append(name)
            indices.append([0])

            for i in range(1, len(names)):
                name = names[i].split('_')[0]
                try:
                    index = atoms.index(name)
                except ValueError: #not found in atom list
                    atoms.append(name)
                    indices.append([i])
                else:
                    indices[index].append(i)

        natoms = len(indices)
        nmocoeffs = len(self.aoresults[0])
        
#build results Numeric array[3]
        if len(self.aoresults) == 2:
            results = Numeric.zeros([2, nmocoeffs, natoms], "f")
        else:
            results = Numeric.zeros([1, nmocoeffs, natoms], "f")
        
#for each spin, splice Numeric array at ao index, and add to correct result row
        for spin in range(len(results)):

            for i in range(natoms): #number of groups

                for j in range(len(indices[i])): #for each group
                
                    temp = self.aoresults[spin, :, indices[i][j]]
                    results[spin, :, i] = Numeric.add(results[spin, :, i], temp)

        self.logger.info("Saving partitioned results in fragresults: array[3]")
        self.fragresults = results

        return True

if __name__ == "__main__":
    import doctest, population
    doctest.testmod(population, verbose=False)
