'''Tools to pull a star's coordinates from SIMBAD and propagate its proper motion to a given epoch.'''
import numpy as np
import astropy.coordinates
import astropy.units
from astroquery.simbad import Simbad

class Star(object):
	def __init__(self):
		pass

class SingleStar(Star):
	def __init__(self, name, pmra=None, pmdec=None):
		Star.__init__(self)
		self.simbad(name)
		if pmra is not None:
			self.pmra = pmra
		if pmdec is not None:
			self.pmdec = pmdec

	def simbad(self, name, pmra=None, pmdec=None):
		containswildcard = "*" in name or "?" in name or "[" in name or "]" in name
		Simbad.reset_votable_fields()
		Simbad.add_votable_fields('pm')
		Simbad.add_votable_fields('sptype')
		Simbad.add_votable_fields('flux(V)')
		Simbad.add_votable_fields('flux(K)')
		self.table = Simbad.query_object(name)


		self.name = self.table['MAIN_ID']
		self.icrs = astropy.coordinates.SkyCoord(self.table['RA'], self.table['DEC'],'icrs', unit=(astropy.units.hourangle, astropy.units.deg))[0]

		self.pmra = self.table['PMRA'].data[0]		# in (projected) milliarcseconds
		self.pmdec = self.table['PMDEC'].data[0]	# in milliarcseconds

	def setEpoch(self, epoch):
		self.epoch = epoch
		self.current = self.atEpoch(self.epoch)

	def atEpoch(self, epoch):

		timeelapsed = epoch - 2000.0	# in years
		rarate = self.pmra/60.0/60.0/np.cos(self.icrs.dec.radian)/1000.0	# in degress of RA/year
		decrate = self.pmdec/60.0/60.0/1000.0	# in degrees/year

		raindegrees = self.icrs.ra.degree + timeelapsed*rarate
		decindegrees = self.icrs.dec.degree + timeelapsed*decrate
		return astropy.coordinates.SkyCoord(raindegrees, decindegrees, 'icrs', unit=(astropy.units.degree, astropy.units.degree))

	def now(self, epoch=None):
		if epoch is None:
			epoch = 2014.75
		self.setEpoch(epoch)
		print self.posstring(coord=self.icrs, epoch=2000.0)
		print " with d(RA)={pmra}, d(Dec)={pmdec} mas of proper motion".format(pmra=self.pmra, pmdec=self.pmdec)
		print self.posstring(coord=self.current, epoch=self.epoch)
		return self.posstring(coord=self.current, epoch=self.epoch).split()

	def posstring(self, coord=None, epoch=None):
		if epoch is None:
			epoch = self.epoch
		if coord is None:
			coord = self.current
		form = '{ra:s} {dec:s} ({epoch:6.1f})'
		rah,ram,ras = coord.ra.hms
		ra = "{h:02.0f}:{m:02.0f}:{s:05.2f}".format(h=rah,m=ram,s=ras)
		decd,decm,decs = coord.dec.dms
		dec="{d:+02.0f}:{m:02.0f}:{s:04.1f}".format(d=decd,m=np.abs(decm),s=np.abs(decs))
		return form.format(ra=ra, dec=dec, epoch=epoch)
