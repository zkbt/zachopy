'''Units, with everything in terms of cgs.'''
import numpy as np

# speeds
c = 29979245800.0

# times
second = 1.0
minute = 60.0*second
hour = 60.0*minute
day = 24.0*hour
century = 36525.0*day
year = century/100.0

# angles
radian = 1.0
degree = np.pi/180.0
arcmin = degree/60.0
arcsec = arcmin/60.0


# distances
cm = 1.0
m = 100.0*cm
nm = 1e-9*m
km = 1000.0*m
Rsun = 695660*km
Rearth = 6378.1366*km
Rjupiter = 71492*km
au = 149597870700.0*m
pc = au/arcsec
ly = c*year


# masses
g = 1.0
kg = 1000.0
Msun = 1.9884e30*kg
Mjupiter = Msun/1.047348644e03
Mearth = Msun/332946.0487
mp = 1.66053892e-27*kg

# energy
erg = g*cm**2/second**2 # (should be 1!)
Joule = 1e7*erg

# power


# temperatures
K = 1.0
Tsun = 5771.8 # Mamajek
k_B = 1.3806488e-23*m**2*kg/second**2/K
sigma_SB = 5.6704e-5*erg/cm**2/second/K**4

# other
G = 6.67428e-11*m**3/kg/second**2
