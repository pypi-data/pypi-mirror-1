import logging
import gamessparser

a = gamessparser.GAMESS("../../../data/GAMESS/basicGAMESS-US/dvb_sp.out")
a.logger.setLevel(logging.ERROR)
a.parse()
print
print len(a.gbasis)
