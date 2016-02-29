'''Generate a finder chart for a star with high proper motion.'''
import matplotlib.pyplot as plt
import numpy as np
from ds9 import *
from astropy.io import ascii
from astropy import coordinates, units
import regions
import zachopy.star
import zachopy.utils
import os
import copy
from slit_mask_regions import slit_mask_regions

finderdir = os.environ['COSMOS'] + 'Finders/'
zachopy.utils.mkdir(finderdir)

class Camera(object):
	def __init__(self,name):
		self.instruments = {}
		self.instruments['LDSS3C'] ={'size':8.0, 'inflate':1.8}
		self.instruments['CHIRON'] ={'size':3.0, 'inflate':1.8}
		self.instruments['PISCO'] ={'size':9.0, 'inflate':1.8}
		self.setup(name)

	def setup(self, name):
		for k in self.instruments[name].keys():
			self.__dict__[k] = self.instruments[name][k]


class Finder(object):
	def __init__(self, 	star,
						moment=2016.3,
						instrument='LDSS3C',
						npixels=500, **starkw):

		'''produce a finder chart for a given star, at a particular moment
				star = either a star object, or the name of star for Simbad
						(**starkw will be passed to the star creation,
						 if you need custom RA, DEC, proper motions)
				moment = for what epoch (e.g. 2016.3) should the chart show?
				instrument = a string, indicating basic size of the chart
				npixels = how big the image can be; ds9 needs all on screen
		'''

		if type(star) == str:
			# if star is a string, use it (and starkw) to create star object
			self.name = star
			self.star = zachopy.star.Star(name, **starkw)
		else:
			# if star isn't a string, it must be a zachopy.star.Star object'''
			self.star = star
			self.name = star.name

		# keep track
		self.instrument = instrument
		self.npixels = npixels

		# define the moment this finder should represent
		self.setMoment(moment)


		# use ds9 to create the finder chart
		self.createChart()

	def setMoment(self, moment):
		self.moment = moment



	def createChart(self):
		self.icrs = self.star.atEpoch(self.moment)
		self.ra, self.dec = self.icrs.ra, self.icrs.dec

		self.camera = Camera(self.instrument)
		self.coordstring = self.icrs.to_string('hmsdms')
		for letter in 'hmdm':
			self.coordstring = self.coordstring.replace(letter, ':')
		self.coordstring = self.coordstring.replace('s', '')

		self.w = ds9()
		self.w.set("frame delete all")
		self.size = self.camera.size
		self.inflate = self.camera.inflate
		#try:
		#	self.addImage('poss1_red')
		#except:
		#	print "poss1 failed"
		#try:
		self.addImage('poss2ukstu_red')
		#except:
		#	print "poss2 failed"

		self.addRegions()

		try:
			slit_mask_regions(self.star.attributes['slits'], 'slits')
			self.w.set("regions load {0}".format('slits.reg'))
		except KeyError:
			print "no slits found!"

		self.tidy()
		self.save()
	def tidy(self):
		self.w.set("tile mode column")
		self.w.set("tile yes")

		self.w.set("single")
		self.w.set("zoom to fit")
		self.w.set("match frame wcs")

	def save(self):
		zachopy.utils.mkdir('finders')
		for d in [finderdir, 'finders/']:
			print "saveimage " + d + self.name.replace(' ', '') + ".png"
			self.w.set("saveimage " + d + self.name.replace(' ', '') + ".png")


	def addImage(self, survey='poss2_red'):
		self.w.set("frame new")
		self.w.set('single')
		self.w.set( "dssstsci survey {0}".format(survey))
		self.w.set("dssstsci size {0} {1} arcmin ".format(self.size*self.inflate, self.size*self.inflate))
		self.w.set("dssstsci coord {0} sexagesimal ".format(self.coordstring))

	def addRegions(self):
		xpixels = self.w.get('''fits header keyword "'NAXIS1'" ''')
		ypixels = self.w.get('''fits header keyword "'NAXIS1'" ''')
		self.scale = np.minimum(int(xpixels), self.npixels)/float(xpixels)
		self.w.set("width {0:.0f}".format(int(xpixels)*self.scale))
		self.w.set("height {0:.0f}".format(int(ypixels)*self.scale))

		# add circles centered on the target position
		r = regions.Regions("LDSS3C", units="fk5", path=finderdir )


		imageepoch = float(self.w.get('''fits header keyword "'DATE-OBS'" ''').split('-')[0])

		old = self.star.atEpoch(imageepoch)
		print imageepoch
		print self.star.posstring(imageepoch)

		current = self.star.atEpoch(self.moment)
		print self.moment
		print self.star.posstring(self.moment)
		r.addLine(old.ra.degree, old.dec.degree, current.ra.degree, current.dec.degree, line='0 1', color='red')
		print old.ra.degree, old.dec.degree, current.ra.degree, current.dec.degree
		r.addCircle(current.ra.degree, current.dec.degree, "{0}'".format(self.size/2), text="{0:.1f}' diameter".format(self.size), font="bold {0:.0f}".format(np.round(self.scale*14.0)))

		r.addCircle(current.ra.degree, current.dec.degree, "{0}'".format(2.0/60.0))

		# add a compass
		radius = self.size/60/2
		r.addCompass(current.ra.degree + 0.95*radius, current.dec.degree + 0.95*radius, "{0}'".format(self.size*self.inflate/10))
		r.addText(current.ra.degree, current.dec.degree - 1.1*radius, self.name + ', ' + self.star.posstring(self.moment), font='bold {0:.0f}'.format(np.round(self.scale*16.0)), color='red')

		r.addText(current.ra.degree - 1.04*radius, current.dec.degree + 1.02*radius, 'd(RA)={0:+3.0f}, d(Dec)={1:+3.0f} mas/yr'.format(self.star.pmra, self.star.pmdec), font='bold {0:.0f}'.format(np.round(self.scale*12.0)),  color='red')

		r.addText(current.ra.degree - 1.04*radius, current.dec.degree + 0.95*radius, '(image from {0})'.format(imageepoch), font='bold {0:.0f}'.format(np.round(self.scale*10.0)),  color='red')
		# load regions into image
		print(r)
		r.write()
		self.w.set("cmap invert yes")
		self.w.set("colorbar no")

		#self.w.set("rotate to {0}".format(int(np.round(90 -63 - self.star['rot'][0]))))
		self.w.set("regions load {0}".format(r.filename))
