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

finderdir = os.environ['COSMOS'] + 'Finders/'
zachopy.utils.mkdir(finderdir)

class Camera(object):
	def __init__(self,name):
		self.instruments = {}
		self.instruments['LDSS3C'] ={'size':6.0, 'inflate':1.3}
		self.instruments['CHIRON'] ={'size':3.0, 'inflate':1.8}
		self.setup(name)
		
	def setup(self, name):
		for k in self.instruments[name].keys():
			self.__dict__[k] = self.instruments[name][k]
		

class Finder(object):
	def __init__(self,name='', ra=None, dec=None, all=False, instrument='CHIRON', pmra=None, pmdec=None):
		self.name = name
		self.star = zachopy.star.SingleStar(name, pmra=pmra, pmdec=pmdec)
		self.ra, self.dec, self.epoch = self.star.now()
		self.coord = self.star.current		
		
		self.camera = Camera(instrument)
		self.coordstring = "{0} {1}".format(self.ra, self.dec)
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
			
		xpixels = self.w.get('''fits header keyword "'NAXIS1'" ''')
		ypixels = self.w.get('''fits header keyword "'NAXIS1'" ''')
		scale = np.maximum(int(xpixels), 1000)/float(xpixels)
		self.w.set("width {0:.0f}".format(int(xpixels)*scale))
		self.w.set("height {0:.0f}".format(int(ypixels)*scale))

		self.w.set("tile mode column")
		self.w.set("tile yes")
		
		self.w.set("single")
		self.w.set("zoom to fit")
		self.w.set("match frame wcs")
		print "saveimage " + finderdir + self.name.replace(' ', '') + ".png"
		self.w.set("saveimage " + finderdir + self.name.replace(' ', '') + ".png")

		
	def addImage(self, survey='poss1_red'):
		self.w.set("frame new")
		self.w.set('single')
		self.w.set( "dssstsci survey {0}".format(survey))
		self.w.set("dssstsci size {0} {1} arcmin ".format(self.size*self.inflate, self.size*self.inflate))
		self.w.set("dssstsci coord {0} sexagesimal ".format(self.coordstring))

		# add circles centered on the target position
		r = regions.Regions("LDSS3C", units="fk5", path=finderdir )


		imageepoch = float(self.w.get('''fits header keyword "'DATE-OBS'" ''').split('-')[0])
		
		old = self.star.atEpoch(imageepoch)
		p = self.star.posstring
		print p(old,imageepoch)
		print p(self.star.current,self.star.epoch)
		current = self.star.current
		r.addLine(old.ra.degree, old.dec.degree, current.ra.degree, current.dec.degree, line='0 1', color='red')
		print old.ra.degree, old.dec.degree, current.ra.degree, current.dec.degree
		r.addCircle(current.ra.degree, current.dec.degree, "{0}'".format(self.size/2), text="{0:.1f}' diameter".format(self.size), font="bold {0:.0f}".format(np.round(14.0)))

		r.addCircle(current.ra.degree, current.dec.degree, "{0}'".format(2.0/60.0))

		# add a compass
		radius = self.size/60/2
		r.addCompass(current.ra.degree + 0.95*radius, current.dec.degree + 0.95*radius, "{0}'".format(self.size*self.inflate/5))
		r.addText(current.ra.degree, current.dec.degree - 1.1*radius, self.name + ', ' + self.star.posstring(), font='bold {0:.0f}'.format(np.round(16.0)), color='red')

		r.addText(current.ra.degree - 1.04*radius, current.dec.degree + 1.02*radius, 'd(RA)={0:+3.0f}, d(Dec)={1:+3.0f} mas/yr'.format(self.star.pmra, self.star.pmdec), font='bold {0:.0f}'.format(np.round(12.0)),  color='red')

		r.addText(current.ra.degree - 1.04*radius, current.dec.degree + 0.95*radius, '(image from {0})'.format(imageepoch), font='bold {0:.0f}'.format(np.round(10.0)),  color='red')
		# load regions into image
		print(r)
		r.write()
		self.w.set("cmap invert yes")
		self.w.set("colorbar no")

		#self.w.set("rotate to {0}".format(int(np.round(90 -63 - self.star['rot'][0]))))
		self.w.set("regions load {0}".format(r.filename))