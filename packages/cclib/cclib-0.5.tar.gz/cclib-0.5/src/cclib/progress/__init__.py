"""
cclib (http://cclib.sf.net) is (c) 2006, the cclib development team
and licensed under the LGPL (http://www.gnu.org/copyleft/lgpl.html).
"""

__revision__ = "$Revision: 240 $"

from textprogress import TextProgress
import sys

if 'qt' in sys.modules.keys():
    from qtprogress import QtProgress
