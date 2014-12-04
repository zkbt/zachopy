import numpy as np
import matplotlib.pyplot as plt
import eb
import zachopy.mpfit
from Planet import Planet
from Star import Star
from Instrument import Instrument
import zachopy.PDF
import zachopy.color
import emcee
import matplotlib.gridspec
import matplotlib.patches
import copy
plt.ion()
ppm = 1e6

class TM(object):
	'''Transit Model object handles generation of model transit light curves.
		(relies heavily on Jonathan Irwin's "eb" code, which is an updated
		implementation of the classic EBOP and JKTEBOP, available at:
			https://github.com/mdwarfgeek'''
	
	def __init__(self, planet=None, star=None, instrument=None, directory=None,depthassumedforplotting=None, **kwargs):
		'''Initialize the parameters of the model.'''
		
		# create an empty array of parameters for eb
		self.ebparams = np.zeros(eb.NPAR, dtype=np.double)	

		# keep track of a depth for plotting, if necessary
		self.depthassumedforplotting=depthassumedforplotting
		
		# define the subsets of the parameters
		if planet is None:
			planet = Planet()
		if star is None:
			star = Star()
		if instrument is None:
			instrument = Instrument()
		self.planet = planet
		self.star = star
		self.instrument = instrument
		
		# load the model, if possible, and if a directory was given
		if directory is not None:
			print "  Attempting to load transit model from ", directory 
			self.load(directory)
			
	def load(self, directory):
		'''Load parameters from directory.'''
		self.planet = Planet(directory=directory)	
		self.star = Star(directory=directory)
		self.instrument = Instrument(directory=directory)
			
	def save(self, directory):
		'''Save parameters to directory.'''
		for x in (self.planet, self.star, self.instrument):
			x.save(directory)
			print "     saving model to {directory}".format(directory=directory)	
		
	def linkLightCurve(self, transitlightcurve):
		'''Attach a model to a light curve, defining all the TM and TLC attributes.'''
		self.TLC = transitlightcurve
		self.TM = self
		self.TLC.TM = self
		self.TLC.TLC = self.TLC
		
	def set_ebparams(self):
		'''Set up the parameters required for eb. '''
		# These are the basic parameters of the model.
		self.ebparams[eb.PAR_J]      =  self.planet.surface_brightness_ratio  # J surface brightness ratio
		self.ebparams[eb.PAR_RASUM]  =  self.planet.rsum_over_a  # (R_1+R_2)/a
		self.ebparams[eb.PAR_RR]     =  self.planet.rp_over_rs  # R_2/R_1
		self.ebparams[eb.PAR_COSI]   =  self.planet.cosi  # cos i

		# Mass ratio is used only for computing ellipsoidal variation and
		# light travel time.  Set to zero to disable ellipsoidal.
		self.ebparams[eb.PAR_Q]      =  self.planet.mass_ratio

		# Light travel time coefficient.
		ktot = 55.602793  # K_1+K_2 in km/s
		cltt = 1000*ktot / eb.LIGHT

		# Set to zero if you don't need light travel correction (it's fairly slow
		# and can often be neglected).
		self.ebparams[eb.PAR_CLTT]   =  cltt#*(self.planet.q.value == 0.0)      # ktot / c

		# Radiative properties of star 1.
		self.ebparams[eb.PAR_LDLIN1] = self.star.u1.value   # u1 star 1
		self.ebparams[eb.PAR_LDNON1] = self.star.u2.value  # u2 star 1
		self.ebparams[eb.PAR_GD1]    = self.star.gd.value     # gravity darkening, std. value
		self.ebparams[eb.PAR_REFL1]  = self.star.albedo.value      # albedo, std. value

		# Spot model.  Assumes spots on star 1 and not eclipsed.
		self.ebparams[eb.PAR_ROT1]   =  1.0# 0.636539  # rotation parameter (1 = sync.)
		self.ebparams[eb.PAR_FSPOT1] =  0.0       # fraction of spots eclipsed
		self.ebparams[eb.PAR_OOE1O]  =  0.0       # base spottedness out of eclipse
		self.ebparams[eb.PAR_OOE11A] =  0.0#0.006928  # *sin
		self.ebparams[eb.PAR_OOE11B] =  0.0 # *cos

		# PAR_OOE12* are sin(2*rot*omega) on star 1,
		# PAR_OOE2* are for spots on star 2.

		# Assume star 2 is the same as star 1 but without spots.
		self.ebparams[eb.PAR_LDLIN2] = self.ebparams[eb.PAR_LDLIN1]
		self.ebparams[eb.PAR_LDNON2] = self.ebparams[eb.PAR_LDNON1]
		self.ebparams[eb.PAR_GD2]    = self.ebparams[eb.PAR_GD1]
		self.ebparams[eb.PAR_REFL2]  = self.ebparams[eb.PAR_REFL1]

		# Orbital parameters.
		self.ebparams[eb.PAR_ECOSW]  =  self.planet.ecosw.value  # ecosw
		self.ebparams[eb.PAR_ESINW]  = self.planet.esinw.value  # esinw
		self.ebparams[eb.PAR_P]      = self.planet.period.value  # period
		self.ebparams[eb.PAR_T0]     = self.planet.t0.value + self.planet.dt.value # T0 (epoch of primary eclipse), with an offset of dt applied
		# OTHER NOTES:
		#
		# To do standard transit models (a'la Mandel & Agol),
		# set J=0, q=0, cltt=0, albedo=0.
		# This makes the secondary dark, and disables ellipsoidal and reflection.
		#
		# The strange parameterization of radial velocity is to retain the
		# flexibility to be able to model just light curves, SB1s, or SB2s.
		#
		# For improved precision, it's best to subtract most of the "DC offset"
		# from T0 and the time array (e.g. take off the nominal value of T0 or
		# the midtime of the data array) and add it back on at the end when
		# printing self.ebparams[eb.PAR_T0] and vder[eb.PAR_TSEC].  Likewise the period
		# can cause scaling problems in minimization routines (because it has
		# to be so much more precise than the other parameters), and may need
		# similar treatment.

	def planet_model(self, tlc=None, t=None):
		'''Model of the planetary transit.'''
		self.set_ebparams()

		if tlc is None:
			tlc = self.TLC
		
		if t is None:
			t = tlc.bjd
		typ = np.empty_like(t, dtype=np.uint8)
		typ.fill(eb.OBS_MAG)
		return 10**(-0.4*eb.model(self.ebparams, t, typ))
	
	def instrument_model(self, tlc=None):
		'''Model of the instrument.'''
		if tlc is None:
			tlc = self.TLC
		return self.instrument.model(tlc)
	
	def model(self, tlc=None):
		'''Model including both instrument and planetary transit.'''
		return self.planet_model(tlc=tlc)*self.instrument_model(tlc=tlc)

	@property
	def parameters(self):
		'''Return a list of the parameters that are variable.'''
		try:
			assert(len(self._parameters) == len(self.floating))
			return self._parameters
		except:
			self.defineParameterList()
			return self._parameters
	
	@parameters.setter
	def parameters(self, **kwargs):
		pass
	
	def defineParameterList(self):
		'''Set up the parameter list, by pulling the variable parameters out of the subsets.'''
	
		# define a list containing the keys all the parameters that float
		self.floating = []
		list = []
		for x in (self.planet, self.star, self.instrument):
			d = x.__dict__
			for key in d.keys():
				if d[key].fixed == False:
					self.floating.append(key)
					list.append(d[key])
		self._parameters = np.array(list)
		
	def	fromArray(self, array):
		'''Use an input array to assign the internal parameter attributes.'''
		count = 0
		for parameter in self.parameters:
			parameter.value = array[count]
			count += 1
	
	def toArray(self):
		'''Define an parameter array, by pulling them out of the internal parameter attributes.'''
		list = []
		parinfolist = []
		for parameter in self.parameters:
			list.append(parameter.value)
			parinfolist.append(parameter.parinfo)
		return list, parinfolist
	
	def plotPhased(self):
		'''Plot the light curve model, phased with the planetary period.'''
		t_phased = self.planet.timefrommidtransit(self.smooth_phased_tlc.bjd)
		assert(len(t_phased) == len(self.model(self.smooth_phased_tlc)))
		try:
			for phased in [self.line_phased[0], self.line_phased_zoom[0]]:
				phased.set_data(t_phased, self.model(self.smooth_phased_tlc))
		except:
			self.line_phased = self.TLC.ax_phased.plot(t_phased,self.model(self.smooth_phased_tlc), **self.kw)
			self.line_phased_zoom = self.TLC.ax_phased_zoom.plot(t_phased, self.model(self.smooth_phased_tlc), **self.kw)

	def plotUnphased(self):		
		'''Plot the light curve model, linear in time.'''
		t_unphased = self.smooth_unphased_tlc.bjd - self.planet.t0.value
		assert(len(t_unphased) == len(self.model(self.smooth_unphased_tlc)))
		try:
			for unphased in [self.line_unphased[0], self.line_unphased_zoom[0]]:
				unphased.set_data(t_unphased, self.model(self.smooth_unphased_tlc))
		except:
			self.line_unphased = self.TLC.ax_unphased.plot(t_unphased, self.model(self.smooth_unphased_tlc), **self.kw)
			self.line_unphased_zoom = self.TLC.ax_unphased_zoom.plot(t_unphased, self.model(self.smooth_unphased_tlc), **self.kw)
							
	def plotDiagnostics(self):		
		'''Plot the light curve model, linear in time.'''
		t_unphased = self.smooth_unphased_tlc.bjd - self.planet.t0.value
		assert(len(t_unphased) == len(self.model(self.smooth_unphased_tlc)))
			
		#try:
		#	self.line_raw.set_data(t_unphased, self.model(self.smooth_unphased_tlc))
		#	self.line_corrected.set_data(t_unphased, self.planet_model(self.smooth_unphased_tlc))
		#	self.line_residuals.set_data(t_unphased, ppm*np.zeros_like(t_unphased))
		#	self.line_instrument.set_data(t_unphased, ppm*self.instrument_model(self.smooth_unphased_tlc))
		#except:
		# NOT USING?!?
		self.line_raw = self.TLC.ax_raw.plot(t_unphased, self.model(self.smooth_unphased_tlc), **kw)[0]
		self.line_corrected = self.TLC.ax_corrected.plot(t_unphased, self.planet_model(self.smooth_unphased_tlc), **kw)[0]
		self.line_residuals = self.TLC.ax_residuals.plot(t_unphased, ppm*np.zeros_like(t_unphased), **kw)[0]
		self.line_instrument = self.TLC.ax_instrument.plot(t_unphased, ppm*self.instrument_model(self.smooth_unphased_tlc), **kw)[0]

	def plot(self):
		'''Plot the model lines over the existing light curve structures.'''
		self.kw = {'color':self.TLC.colors['lines'], 'linewidth':3, 'alpha':1.0}
		self.plotPhased()
		self.plotUnphased()

		if self.depthassumedforplotting is None:
			self.depthassumedforplotting = self.planet.rp_over_rs.value**2

		# need to work on displaying the parameters...
		try:
			xtext = self.planet.duration/2.0*1.1
			posttransit = self.planet.timefrommidtransit(bjd) > self.planet.duration/2.0
			ytext = np.mean(self.model()[posttransit]) - self.planet.rp_over_rs**2/2.0
			instrument_string = "Instrumental Parameters"
			self.TLC.ax_raw.text(xtext, ytext, instrument_string)
		except:
			pass
		
	def deviates(self, p, fjac=None, plotting=False):
		'''Return the normalized deviates (an input for mpfit).'''
		
		# populate the parameter attributes, using the input array
		self.fromArray(p)

		# if necessary, plot the light curve along with this step of the deviates calculation
		status =0
		if plotting:
			self.TLC.LightcurvePlots()
			
		ok = (self.TLC.bad == 0).nonzero()
		
		devs = (self.TLC.flux[ok] - self.TM.model()[ok])/self.TLC.error[ok]
		
		# add limb darkening priors
		try:
			prioru1 = (self.star.u1.value - self.u1prior_value)/self.u1prior_uncertainty
			prioru2 = (self.star.u2.value - self.u2prior_value)/self.u2prior_uncertainty
			devs = np.append(devs, prioru1)
			devs = np.append(devs, prioru2)
			print '==============================='
			print 'u1: ({value} - {center})/{uncertainty}'.format(value = self.star.u1.value, center=self.u1prior_value, uncertainty =self.u1prior_uncertainty)
			print 'u2: ({value} - {center})/{uncertainty}'.format(value = self.star.u2.value, center=self.u2prior_value, uncertainty =self.u2prior_uncertainty)
		
		except:
			pass
			
		# mpfit wants a list with the first element containing a status code 
		return [status,devs]

	def fastfit(self, plot=False, quiet=True, ldpriors=True):
		'''Use LM (mpfit) to find the maximum probability parameters, and a covariance matrix.'''
	
		self.floating = []
		for x in (self.planet, self.star, self.instrument):
			d = x.__dict__
			for key in d.keys():
				if d[key].fixed == False:
					self.floating.append(key)
		
		if ldpriors:
			self.u1prior_value = self.star.u1.value + 0.0
			self.u2prior_value = self.star.u2.value + 0.0
			self.u1prior_uncertainty = self.star.u1.uncertainty + 0.0
			self.u2prior_uncertainty = self.star.u2.uncertainty + 0.0
			
		# pull out the parameters into an array for mpfit
		p0, parinfo = self.toArray()	
		
		# perform the LM fit, to get best fit parameters and covariance matrix		
		self.mpfitted = zachopy.mpfit.mpfit(self.deviates, p0, parinfo=parinfo, quiet=quiet)
		
		# set the parameters to their fitted values			
		for i in range(len(self.parameters)):
			self.parameters[i].value = self.mpfitted.params[i]

		# determine the uncertainties, including a rescaling term
		self.chisq = np.sum((self.TLC.residuals()/self.TLC.error)**2)
		self.dof = self.mpfitted.dof
		self.rescaling = np.maximum(np.sqrt(self.chisq/self.dof), 1)
		print self.rescaling

		self.covariance = self.mpfitted.covar*self.rescaling**2
		for i in range(len(self.parameters)):
			self.parameters[i].uncertainty = np.sqrt(self.covariance[i, i])
	
		# plot the fit
		#self.TLC.DiagnosticsPlots()
		#self.TM.plot()
		
		# pull out the parameters that actually varied, and plot their PDF
		interesting = (self.covariance[range(len(self.parameters)), range(len(self.parameters))] > 0).nonzero()[0]		
		if plot:
			self.pdf_fast = zachopy.PDF.PDF(parameters=self.parameters[interesting], covariance=self.covariance[interesting,:][:,interesting])
			self.pdf_fast.plot()

	def lnprob(self, p):
		lnlikelihood = -np.sum(self.deviates(p)[-1]**2)/2.0
		constraints = 0.0
		for parameter in self.parameters:
			inside = (parameter.value < np.max(parameter.limits)) & (parameter.value > np.min(parameter.limits))
			if inside:
				pass
			else:
				constraints -= 1e6
		return lnlikelihood + constraints

	def slowfit(self, usecovariance=False, broad=True, nwalkers=100, nsteps=1000):
		'''Use affine-invariant MCMC (the emcee) to sample from the parameter probability distribution.'''



		# pull out the parameters into an array for mpfit
		p0, parinfo = self.toArray()	
		nparameters = len(p0)
		nwalkers = 100
		
		if usecovariance:
			# make sure that a fast fit exists
			try:
				self.pdf_fast
			except:
				self.fastfit(floating)
		
		# setup the initial walker positions
		initialwalkers = np.zeros((nwalkers, nparameters))
		for i in range(nparameters):	
			parameter = self.parameters[i]
			if usecovariance:
				initialwalkers[:,i] = self.pdf_fast.samples[parameter.name][0:nwalkers]
			else:
				initialwalkers[:,i] = np.random.uniform(parameter.limits[0], parameter.limits[1], nwalkers)
			
		
		# set up the emcee sampler
		self.sampler = emcee.EnsembleSampler(nwalkers, nparameters, self.lnprob)
		
		
		step = 100
		# run a burn in step, and then reset
		burnt = False
		while burnt == False:
			print "Running {0} burn-in steps, with {1} walkers.".format(step, nwalkers)
			pos, prob, state = self.sampler.run_mcmc(initialwalkers, step)
			samples = {}
			for i in range(nparameters):
				samples[self.floating[i]] = self.sampler.flatchain[:,i]
			self.pdf_slow = zachopy.PDF.PDF(samples=samples)#, covariance=self.pdf_fast.covariance)
			self.pdf_slow.plot(subsample=10000)
			answer = raw_input('Do you think we have burned in?')
			if 'y' in answer:
				burnt = True
		self.sampler.reset()
	
		leap = step*10
		finished = False
		while finished == False:
			print "Running {0} steps with {1} walkers.".format(leap, nwalkers)
			
			# start with the last set of walker positions from the burn in and run for realsies
			self.sampler.run_mcmc(pos, leap)
		
			ok = self.sampler.flatlnprobability > (np.max(self.sampler.flatlnprobability) - 100)
			samples = {}
			for i in range(nparameters):
				samples[self.floating[i]] = self.sampler.flatchain[ok,i]
		
			#best = self.sampler.flatchain[np.argmax(self.sampler.flatlnprobability)]
			best = self.sampler.flatchain[np.random.choice(ok.nonzero()[0])]
			print best
			self.fromArray(best)
			self.TLC.LightcurvePlots()
			plt.draw()
			
			self.chisq = -2*self.lnprob(best)
			self.dof = len(self.TLC.bjd) - len(self.floating)
			self.reduced_chisq = self.chisq/self.dof
			print self.chisq, self.dof, self.reduced_chisq
			
			self.pdf_slow = zachopy.PDF.PDF(samples=samples)#, covariance=self.pdf_fast.covariance)
			self.pdf_slow.plot(subsample=10000)
			plt.draw()
			np.save('temporary_pdf.npy', samples)
			a = raw_input('Are you satisfied?')
			if 'y' in a:
				finished = True
