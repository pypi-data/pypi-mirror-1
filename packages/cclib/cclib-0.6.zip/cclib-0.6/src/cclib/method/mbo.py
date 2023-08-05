"""
cclib (http://cclib.sf.net) is (c) 2006, the cclib development team
and licensed under the LGPL (http://www.gnu.org/copyleft/lgpl.html).
"""

__revision__ = "$Revision: 238 $"

import Numeric
import random # For sometimes running the progress updater
from density import Density

class MBO(Density):
    """Calculate the density matrix"""
    def __init__(self, *args):

        # Call the __init__ method of the superclass
        super(MBO, self).__init__(logname="MBO", *args)
        
    def __str__(self):
        """Return a string representation of the object."""
        return "Mayer's bond order of" % (self.parser)

    def __repr__(self):
        """Return a representation of the object."""
        return 'Mayer\'s bond order("%s")' % (self.parser)
    
    def calculate(self, indices=None, fupdate=0.05):
        """Calculate Mayer's bond orders given the results of a parser"""
    
        if not self.parser.parsed:
            self.parser.parse()

        retval = super(MBO, self).calculate(fupdate)
        if not retval: #making density didn't work
            return False

        #do we have the needed info in the parser?
        if not (hasattr(self.parser, "aooverlaps")
                or hasattr(self.parser, "fooverlaps")):
            self.logger.error("Missing overlap matrix")
            return False #let the caller of function know we didn't finish

        if not indices:
#build list of groups of orbitals in each atom for atomresults
            if hasattr(self.parser, "aonames"):
                names = self.parser.aonames
                overlaps = self.parser.aooverlaps
            elif hasattr(self.parser, "fonames"):
                names = self.parser.fonames
                overlaps = self.parser.fooverlaps
            else:
                self.logger.error("Missing aonames or fonames")
                return False

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
#done building list

        self.logger.info("Creating attribute fragresults: array[3]")
        size = len(indices)
        unrestricted = (len(self.parser.mocoeffs) == 2)

        #determine number of steps, and whether process involves beta orbitals
        PS = []
        PS.append(Numeric.matrixmultiply(self.density[0], overlaps))
        nstep = size**2 #approximately quadratic in size
        if unrestricted:
            self.fragresults = Numeric.zeros([2, size, size], "f")
            PS.append(Numeric.matrixmultiply(self.density[1], overlaps))
        else:
            self.fragresults = Numeric.zeros([1, size, size], "f")

        #intialize progress if available
        if self.progress:
            self.progress.initialize(nstep)

        step = 0
        for i in range(len(indices)):

            if self.progress and random.random() < fupdate:
                self.progress.update(step, "Mayer's Bond Order")

            for j in range(i+1, len(indices)):

                tempsumA = 0
                tempsumB = 0
                
                for a in indices[i]:

                    for b in indices[j]:

                        tempsumA += 2 * PS[0][a][b] * PS[0][b][a]
                        if unrestricted:
                            tempsumB += 2 * PS[1][a][b] * PS[1][b][a]

                self.fragresults[0][i, j] = tempsumA
                self.fragresults[0][j, i] = tempsumA

                if unrestricted:
                    self.fragresults[1][i, j] = tempsumB
                    self.fragresults[1][j, i] = tempsumB

        if self.progress:
            self.progress.update(nstep, "Done")

        return True
