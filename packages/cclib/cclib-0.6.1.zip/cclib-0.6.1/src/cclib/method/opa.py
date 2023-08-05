"""
cclib (http://cclib.sf.net) is (c) 2006, the cclib development team
and licensed under the LGPL (http://www.gnu.org/copyleft/lgpl.html).
"""

__revision__ = "$Revision: 361 $"

import Numeric
import random # For sometimes running the progress updater
from calculationmethod import Method

def func(x):
    if x==1:
        return 1
    else:
        return x+func(x-1)

class OPA(Method):
    """The overlap population analysis"""
    def __init__(self, *args):

        # Call the __init__ method of the superclass
        super(OPA, self).__init__(logname="OPA", *args)
        
    def __str__(self):
        """Return a string representation of the object."""
        return "OPA of" % (self.parser)

    def __repr__(self):
        """Return a representation of the object."""
        return 'OPA("%s")' % (self.parser)
    
    def calculate(self, indices=None, fupdate=0.05):
        """Perform an overlap population analysis given the results of a parser"""
    
        if not self.parser.parsed:
            self.parser.parse()

        #do we have the needed info in the parser?
        if not hasattr(self.parser, "mocoeffs") \
          and not ( hasattr(self.parser, "aooverlaps") \
                    or hasattr(self.parser, "fooverlaps") ) \
          and not hasattr(self.parser, "nbasis"):
            self.logger.error("Missing mocoeffs, aooverlaps/fooverlaps or nbasis")
            return False #let the caller of function know we didn't finish

        unrestricted = (len(self.parser.mocoeffs) == 2)
        nmocoeffs = len(self.parser.mocoeffs[0])
        nbasis = self.parser.nbasis

        if not indices:
#build list of groups of orbitals in each atom for atomresults
            if hasattr(self.parser, "aonames"):
                names = self.parser.aonames
            elif hasattr(self.parser, "foonames"):
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

        #determine number of steps, and whether process involves beta orbitals
        nfrag = len(indices) #nfrag
        nstep = func(nfrag - 1)
        self.logger.info("Creating attribute results: array[4]")
        if unrestricted:
            results = Numeric.zeros([2, nfrag, nfrag, nmocoeffs], "f")
            nstep *= 2
        else:
            results=Numeric.zeros([1, nfrag, nfrag, nmocoeffs], "f")

        if hasattr(self.parser, "aooverlaps"):
            overlap = self.parser.aooverlaps
        elif hasattr(self.parser,"fooverlaps"):
            overlap = self.parser.fooverlaps

        #intialize progress if available
        if self.progress:
            self.progress.initialize(nstep)

        size = len(self.parser.mocoeffs[0])
        step = 0

        preresults = []
        two = Numeric.array([2.0]*nmocoeffs,"f")
        for spin in range(len(self.parser.mocoeffs)):


            # OP_{AB,i} = \sum_{a in A} \sum_{b in B} 2 c_{ai} c_{bi} S_{ab}

            for A in range(len(indices)-1):

                for B in range(A+1, len(indices)):

                    if self.progress: #usually only a handful of updates, so remove random part
                        self.progress.update(step, "Overlap Population Analysis")

                    for a in indices[A]:

                        ca = self.parser.mocoeffs[spin,:,a]

                        for b in indices[B]:
                            
                            cb = self.parser.mocoeffs[spin,:,b]
                            temp = ca * cb * two *overlap[a,b]
                            results[spin,A,B] = Numeric.add(results[spin,A,B],temp)
                            results[spin,B,A] = Numeric.add(results[spin,B,A],temp)

                    step += 1

        temparray2 = Numeric.swapaxes(results,2,3)
        self.results = Numeric.swapaxes(temparray2,1,2)

        if self.progress:
            self.progress.update(nstep, "Done")

        return True

if __name__ == "__main__":
    import doctest, opa
    doctest.testmod(opa, verbose=False)
