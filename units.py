'''Units, with everything in terms of cgs.'''
from astropy.units import *

# from Mamajek (https://sites.google.com/site/mamajeksstarnotes/basic-astronomical-data-for-the-sun)
Rsun = Unit('Rsun', 695660*km)
Teffsun = Unit('Teffsun', 5771.8*K)

# from IAU 2009
Rearth = Unit('Rearth', 6378.1366*km)
Rjupiter = Unit('Rjupiter', 71492*km)

Msun = Unit('Msun', 1.9884e30*kg)
Mjupiter = Unit('Mjupiter', Msun/1.047348644e03)
Mearth = Unit('Mearth', Msun/332946.0487)
