import numpy as np
import matplotlib.pyplot as plt
import fast_ma
import copy
import pylab
import astropy.time.Time

plt.ion()

class TLC:
	# define a Transit Light Curve object, that stores everything you need to know about a light curve
	def __init__(self, bjd, flux, fluxerr=None, orbit=None, visit=None, scan=None):
		# how many data points are in light curve?
		self.n = len(bjd)

		# define basic light curve variables
		self.bjd = np.array(bjd)
		self.flux = np.array(flux)
		self.flux /= np.median(flux)
		if fluxerr is None:
			fluxerr = np.ones_like(self.flux)
		else:
			self.fluxerr = np.array(fluxerr)
			
		# if an orbit has been set, define t_orb
		'''if orbit is not None:
			self.orbit = np.array(orbit)
			self.t_orb = np.zeros(self.n)
			u = np.unique(orbit)
			for o in u:
				mask = (orbit == o)
				self.t_orb[mask] = bjd[mask] - bjd[mask].min()

		# if an orbit has been set, define t_orb
		if visit is not None:
			self.t_vis = np.zeros(self.n)
			u = np.unique(visit)
			for v in u:
				mask = (visit == v)
				self.t_vis[mask] = bjd[mask] - bjd[mask].min()'''
					
	def plot(self):
		a = plt.gca()
		a.scatter(self.bjd, self.flux, marker='.')
		plt.draw()
		
class TM:
	# define a Transit Model object, which can be used with fitting a TLC
	
	
	def __init__(self, e=0.0, a_over_rs=15.25, b=0.0, u1=0.1, u2 = 0.1, rp_over_rs=0.1, w=np.pi/2.0, period=1.58, t0=0.0):
		# set the planet parameters
		self.planet = {\
			'e':e, \
			'a_over_rs':a_over_rs, \
			'b':b, \
			'u1':u1, \
			'u2':u2, \
			'rp_over_rs':rp_over_rs, \
			'w':w, \
			'period':period, \
			't0':t0}
		
		# set which of the planet parameters should be fitted and which fixed
		#self.planet_fitted = copy.deepcopy(self.planet)
		#for key in self.planet_fitted.keys():
		#	self.planet_fitted[key] = True
		#self.planet_fitted['w'] = False
			
		# set the instrument parameters
		self.instrument = {\
			'C':1.0, \
			'T1':0.1, \
			'T2':0.01}

		# set which of the instrument parameters should be fitted and which fixed
		#self.instrument_fitted = copy.deepcopy(self.instrument)
		#for key in self.instrument_fitted.keys():
		#	self.instrument_fitted[key] = True
		
		# set which of the parameters should be fitted and which fixed
		self.parameters = copy.deepcopy(self.planet)
		self.parameters.update(copy.deepcopy(self.instrument))
		self.fitted = copy.deepcopy(self.parameters)
		for key in self.fitted.keys():
			self.fitted[key] = True
		self.fitted['a_over_rs'] = False
		self.fitted['b'] = False
		self.fitted['e'] = False
		self.fitted['w'] = False
		self.fitted['u1'] = False
		self.fitted['u2'] = False
		self.fitted['period'] = False
		self.fitted['t0'] = False
	
		
		# set up plot window
		self.figure = plt.figure(figsize=(7,11))

		left, bottom = 0.1, 0.1
		right, top = left, bottom

		width, upperheight = (1-left-right), 0.35
		lowerheight = 1 - upperheight*2 - top - bottom

		self.axes_raw = self.figure.add_axes([left, bottom+lowerheight+upperheight, width, upperheight])
		self.axes_corrected = self.figure.add_axes([left, bottom+lowerheight, width, upperheight], sharex=self.axes_raw, sharey=self.axes_raw)
		self.axes_residuals = self.figure.add_axes([left, bottom, width, lowerheight], sharex=self.axes_raw)
		
			
	def get_fitted(self):
		array = np.array(self.parameters.values())
		keys = np.array(self.parameters.keys())
		mask = np.array(self.fitted.values())
		return array[mask], keys[mask]
	
	def set_fitted(self, input_parameters, input_keys):
		count = 0
		for key in input_keys:
			#print key, self.parameters[key] , '->', input_parameters[count]
			self.parameters[key] = input_parameters[count]
			count += 1
		
	def timefrommidtransit(self, bjd):
		epoch = np.round((bjd - self.parameters['t0'])/self.parameters['period'])
		return bjd - epoch*self.parameters['period'] - self.parameters['t0']
			
	def planet_lc(self, tlc):
	
		times = tlc.bjd
		eps = 1.0e-7			# e min
		e = self.parameters['e']
		w = self.parameters['w']
		a_over_rs = self.parameters['a_over_rs']
		b = self.parameters['b']
		i = np.arccos(b/a_over_rs*(1.0 + e*np.sin(w))/(1.0 - e**2))
		u1 = self.parameters['u1']
		u2 = self.parameters['u2']
		rp_over_rs = self.parameters['rp_over_rs']
		period = self.parameters['period']
		t0 = self.parameters['t0']
		return fast_ma.lc(e, a_over_rs, i, u1, u2, rp_over_rs, w, period, t0, eps, times)
	
	def instrument_lc(self, tlc):
		if True:		
			C = self.parameters['C']
			T1 = self.parameters['T1']
			T2 = self.parameters['T2']
			t = tlc.bjd - np.mean(tlc.bjd)# self.parameters['t0']
			return (C + T1*t + T2*t**2)
		else:
			return np.ones(tlc.n)
				
	def lc(self, tlc):
		return self.planet_lc(tlc)*self.instrument_lc(tlc)
		
	def plot(self, tlc):
	
		#		times = tlc.bjd
		#		x_smooth = np.linspace(min(times), max(times), 1000)
		plt.ion()
		plt.sca(self.axes_raw)
		for a in [self.axes_raw, self.axes_corrected, self.axes_residuals]:
			a.cla()
		
		x = self.timefrommidtransit(tlc.bjd)
		self.axes_raw.scatter(x, self.lc(tlc),marker='.', color='green', alpha=0.3)
		self.axes_raw.scatter(x, tlc.flux, marker='.', color='black', alpha=0.5)
		
		self.axes_corrected.scatter(x, self.planet_lc(tlc),marker='.', color='green', alpha=0.3)
		self.axes_corrected.scatter(x, tlc.flux/self.instrument_lc(tlc), marker='.', color='black', alpha=0.5)
	
		self.axes_residuals.scatter(x, np.zeros(tlc.n) , marker='.', color='green', alpha=0.3)
		self.axes_residuals.scatter(x, tlc.flux - self.lc(tlc), marker='.', color='black', alpha=0.5)
		
		#self.axes_raw.set_xlim(x.min(), x.max())
		#self.axes_raw.set_ylim(tlc.flux.min(), tlc.flux.max())
		#self.axes_residuals.set_ylim((tlc.flux - self.lc(tlc)).min(), (tlc.flux - self.lc(tlc)).max())
		
		plt.draw()
	
	def timefrommidtransit(self, time, zerocenter=True):
		phased = ((time - self.parameters['t0'])%self.parameters['period'])/self.parameters['period']
		if zerocenter:
			phased[phased > 0.5] -= 1.0
		return phased*24.0*60.0*self.parameters['period']
		
	def whichtransit(self, time):
		which = np.median(np.round((time - self.parameters['t0'])/self.parameters['period']))
		bjd = which*self.parameters['period'] +  self.parameters['t0']
		t = astropy.time.Time(bjd, format='jd', scale='tdb')
		print "transit #: ", which
		print 'BJD: ', bjd
		print 'UT: ', t.iso
		
		
	def residuals(self, tlc):
		#tlc.plot()
		#self.plot(tlc)
		model = self.lc(tlc)
		residuals = (tlc.flux - model)/tlc.fluxerr
		return residuals		
		
	def lnprob(self, parameters, keys, tlc):
	
		# you have to be okay with the tm variable getting messed around with
		self.set_fitted(parameters, keys)

		lnprob = 0.0
		#print self.parameters
		# likelihood of data
		residuals = self.residuals(tlc)
		
		if np.random.random() < 0.0001:
			self.plot(tlc)
		lnprob -= 0.5*(residuals**2).sum()
		#print lnprob
		
		return lnprob