"""
cclib (http://cclib.sf.net) is (c) 2006, the cclib development team
and licensed under the LGPL (http://www.gnu.org/copyleft/lgpl.html).
"""

__revision__ = "$Revision: 777 $"
__version__ = "0.8"

import parser
import progress
import method
import bridge

# The test module can be imported if it was installed with cclib.
try:
    import test
except:
    pass
