import logging
import jaguarparser

a = jaguarparser.Jaguar("../../../data/Jaguar/basicJaguar4.2/dvb_sp_b.out")
a.logger.setLevel(logging.ERROR)
a.parse()
print a.gbasis