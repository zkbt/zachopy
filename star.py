'''a "Star" object to keep track of positions and propagate proper motions'''

import numpy as np
import astropy.coordinates
import astropy.units as u
from astroquery.simbad import Simbad

# these are options for how the posstring can be represented
possible_delimiters = ['letters', ' ', ':']

class Star(object):
	def __init__(self,  name=None, ra=None, dec=None, **kw):
		'''Initialize the star, gathering its data from Simbad;
			if you supply...
				ra and dec (with astropy units attached)
				pmra and pmdec (in sky-projected mas/year) and epoch
			they will be used instead of the Simbad values.'''

		# decide how to initialize: use coordinates? or use simbad? or else?
		if ra is not None and dec is not None:
			# create the star from the input coordinates
			self.fromCoords(ra=ra, dec=dec, name=name, **kw)
		elif name is not None:
			# create the star from Simbad, searching on name
			self.fromSimbad(name, **kw)
		else:
			raise ValueError('please call {0}() either with "name" or "ra" + "dec" defined'.format(self.__class__.__name__))

	@property
	def n(self):
		'''return the length of the arrays (maybe multiple stars as one)'''
		return np.size(self.icrs)

	def __repr__(self):
		'''how should this star object be represented?'''
		return '<{0}>'.format(self.name)

	def fromCoords(self, ra=None, dec=None, name=None, unit=(None,None),
					pmra=None, pmdec=None, epoch=None, **attributes):
		"""
			[ra] and [dec] must have units associated with them, either as
				ra=359.0*u.deg, dec=89.0*u.deg
				or
				ra="23:59:59",dec="+89:59:59",unit=(u.hourangle, u.deg)
				or
				ra='23h59m59s +89d59m59s'
				(this last one will figure out the dec, if you leave dec=None)
			[name] can be any name you want to give the star
			[pmra] and [pmdec] are the proper motions, in sky-projected mas/yr
			[epoch] is the time, in decimal years, at which the coordinates
					are reported. extrapolated positions at other epochs will
					use the time difference relative to this date.
			[unit] (optional) keyword passed to SkyCoord, for ra/dec
			[**attributes] other properties of the star to store (e.g. V mag.)
		"""

		# set the star's name, and its attributes
		self.name = name
		self.attributes=attributes

		# we're going to store the epoch as the coordinate's "obstime"
		try:
			# if an epoch is set, convert it from (e.g. 2015.4) to a Time
			obstime=astropy.time.Time(epoch, format='decimalyear')
		except ValueError:
			# if no epoch is set, ignore it
			obstime=None

		# create a coordinate object, and assign the epoch as its "obstime"
		self.icrs = astropy.coordinates.SkyCoord(ra, dec,
						obstime=obstime, unit=unit)

		# if you're supplying proper motions, you better supply an epoch too!
		if (pmra is not None) or (pmdec is not None):
			assert(epoch is not None)

		# keep track of the proper motions
		self.pmra, self.pmdec = pmra, pmdec
		for pm in [self.pmra, self.pmdec]:
			bad = np.isfinite(pm) == False
			try:
				pm[bad] = 0.0
			except TypeError:
				if bad:
					self.pmra, self.pmdec = 0.0, 0.0

		# make sure all the proper motions are finite!
		assert(np.isfinite(self.pmra).all())
		print ' made {0} from custom values'.format(self)

	def fromSimbad(self, name, **attributes):
		'''search for a star name in Simbad, and pull down its data'''

		# add a few extra pieces of information to the search
		Simbad.reset_votable_fields()
		Simbad.add_votable_fields('pm')
		Simbad.add_votable_fields('sptype')
		Simbad.add_votable_fields('flux(V)')
		Simbad.add_votable_fields('flux(K)')

		# send the query to Simbad
		self.table = Simbad.query_object(name)

		# pull out the official Simbad name
		self.name = name
		self.simbadname = self.table['MAIN_ID']

		ra = self.table['RA'].data[0]
		dec = self.table['DEC'].data[0]
		obstime = astropy.time.Time(2000.0, format='decimalyear')
		self.icrs = astropy.coordinates.SkyCoord(ra, dec,
												unit=(u.hourangle, u.deg),
												frame='icrs', obstime=obstime)

		self.pmra = self.table['PMRA'].data[0] 		# in (projected) mas/yr
		self.pmdec = self.table['PMDEC'].data[0]	# in mas/yr

		self.attributes = {}
		self.attributes['V'] = float(self.table['FLUX_V'].data[0])
		self.attributes['comment'] = self.table['SP_TYPE'].data[0]
		for k, v in attributes.iteritems():
			self.attributes[k] = v
		print ' made {0} from SIMBAD'.format(self)

	def atEpoch(self, epoch, format='decimalyear'):
		'''return the positions, at a particular epoch
			[epoch] is by default decimal years
				but other formats are OK if you change format'''

		# set the desired new time
		desiredtime = astropy.time.Time(epoch, format=format)

		# how much time has elapsed?
		try:
			timeelapsed = (desiredtime - self.icrs.obstime).to('year').value
		except:
			timeelapsed = 0.0
			print 'UH-OH! It looks like no proper motion epoch was defined.'
			print '  Returning input coordinates.'

		# at what rate do the coordinates change?
		rarate = self.pmra/60.0/60.0/np.cos(self.icrs.dec.radian)/1000.0
			# in degress of RA/year
		decrate = self.pmdec/60.0/60.0/1000.0
			# in degrees/year

		# update ra and dec, based on the time elapsed
		raindegrees = self.icrs.ra.degree + timeelapsed*rarate
		decindegrees = self.icrs.dec.degree + timeelapsed*decrate

		# create new coordinate object, and return it
		extrapolated = astropy.coordinates.SkyCoord(raindegrees*u.deg,
									decindegrees*u.deg, frame='icrs',
									obstime=desiredtime)
		return extrapolated

	def posstring(self, epoch=2000.0, coord=None, delimiter='letters'):
		'''return a position string, at a particular epoch, for one star'''

		# make sure the delimiter is okay
		assert(delimiter in possible_delimiters)

		# the overall format
		overallform = '{ra:s} {dec:s} ({epoch:6.1f})'

		# extrapolate to the epoch
		coord = self.atEpoch(epoch)

		# pull out the RA and dec
		rah,ram,ras = coord.ra.hms
		decd,decm,decs = coord.dec.dms
		assert(np.isfinite(rah))

		# decide on the string formats
		if delimiter == 'letters':
			raform = "{h:02.0f}h{m:02.0f}m{s:05.2f}s"
			decform = "{d:+03.0f}d{m:02.0f}m{s:04.1f}s"
		else:
			raform = "{h:02.0f}:{m:02.0f}:{s:05.2f}".replace(':', delimiter)
			decform = "{d:+03.0f}:{m:02.0f}:{s:04.1f}".replace(':', delimiter)

		# create the strings, and return the combined one
		ra = raform.format(h=rah,m=ram,s=ras)
		dec = decform.format(d=decd,m=np.abs(decm),s=np.abs(decs))
		return overallform.format(ra=ra, dec=dec, epoch=epoch)
