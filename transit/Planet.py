from Parameters import Parameters
import eb
import numpy as np

class Planet(Parameters):
	'''Parameters (both set and calculated) describing a planet.'''
	def __init__(self, **kwargs):
	
		# define defaults
		Parameters.__init__(self, 	J=0.0, \
									k=0.1, \
									rs_over_a=1.0/10.0, \
									b=0.0, \
									q=0.0, \
									period=10.0, \
									t0=2456000.0, \
									dt=0.0, \
									esinw=0.0, \
									ecosw=0.0)
		
		# overwrite defaults with input keywords
		Parameters.__init__(self, **kwargs)
		
		# set up the parameter constraints
		self.J.parinfo['limited'] = [True, False]
		self.J.parinfo['limits'] = [0, 100]
		
		self.b.parinfo['limited'] = [True, True]
		self.b.parinfo['limits'] = [0.0, 1.0]

		self.q.parinfo['limited'] = [True, False]
		self.q.parinfo['limits'] = [0, 100]
		
		self.period.parinfo['limited'] = [True, False]
		self.period.parinfo['limits'] = [0, 100]

		self.t0.parinfo['limited'] = [True, False]
		self.t0.parinfo['limits'] = [0, 1000000000]



	@property
	def surface_brightness_ratio(self):
		return self.J


	@property
	def mass_ratio(self):
		return self.q			

	@property
	def rp_over_rs(self):
		return self.k
		
	@property
	def depth(self):
		return self.rp_over_rs.value**2
		
	@property
	def a_over_rs(self):
		return 1.0/self.rs_over_a.value
		
	@property
	def rsum_over_a(self):
		#by definition of k = rp/rs
		k = self.k.value
		rs_over_a = self.rs_over_a.value		
		return (1.0 + k)*rs_over_a
		
	@property
	def e(self):
		return np.sqrt(self.esinw.value**2 + self.ecosw.value**2)
		
	@property
	def cosi(self):
		# from Winn (2010)
		b = self.b.value
		rs_over_a = self.rs_over_a.value
		e = self.e
		esinw = self.esinw.value
		return b*rs_over_a*(1.0 + esinw)/(1-e**2)
		
	@property
	def sini(self):
		return np.sqrt(1 - self.cosi**2)

	
	@property
	def duration(self):
		'''duration from 1st to 4th contact (in days)'''
		phasecontacts = self.contacts()
		return (phasecontacts[1] - (phasecontacts[0] - 1))*self.period.value

	def contacts(self):
		return eb.phicont(self.esinw.value, self.ecosw.value, self.cosi, self.rsum_over_a)

	def thismidtransit(self, bjd):
		return np.round((bjd - self.t0.value)/self.period.value)*self.period.value + self.t0.value
		
	def timefrommidtransit(self, bjd):
		'''Calculate the time from the assigned mid-transit time.'''
		phasedtime = (bjd - self.thismidtransit(bjd))
		mask = phasedtime > 0.5*self.period.value
		phasedtime[mask] -= self.period.value
		return phasedtime