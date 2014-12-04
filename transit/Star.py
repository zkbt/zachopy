from Parameters import Parameters
import numpy as np

class Star(Parameters):
	def __init__(self, **kwargs):
		Parameters.__init__(self, u1=0.2, u2=0.6, gd=0.32, albedo=0, mass=0.25)
		Parameters.__init__(self, **kwargs)
		
		self.u1.parinfo['limited'] = [True, True]
		self.u1.parinfo['limits'] = [0, 1]

		self.u2.parinfo['limited'] = [True, True]
		self.u2.parinfo['limits'] = [0, 1]