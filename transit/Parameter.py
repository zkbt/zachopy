import numpy as np

class Parameter(object):
	'''An object to handle everything related to a parameter, aiming to be useful either as an input to mpfit or to my MCMC codes.'''

	
	def __init__(self, name=None, value=None):        
		"""
		'value' - the starting parameter value (but see the START_PARAMS
				 parameter for more information).
		"""
		self.value = value

		"""
		'fixed' - a boolean value, whether the parameter is to be held
				 fixed or not.  Fixed parameters are not varied by
				 MPFIT, but are passed on to MYFUNCT for evaluation.
		"""
		self.fixed = True

		"""
		'limited' - a two-element boolean array.  If the first/second
				   element is set, then the parameter is bounded on the
				   lower/upper side.  A parameter can be bounded on both
				   sides.  Both LIMITED and LIMITS must be given
				   together.
		"""
		self.limited = [False, False]
	
		"""
		'limits' - a two-element float array.  Gives the
				  parameter limits on the lower and upper sides,
				  respectively.  Zero, one or two of these values can be
				  set, depending on the values of LIMITED.  Both LIMITED
				  and LIMITS must be given together.
		"""
		self.limits = [-1.0e6, 1.0e6]

		"""
		'parname' - a string, giving the name of the parameter.  The
				   fitting code of MPFIT does not use this tag in any
				   way.  However, the default iterfunct will print the
				   parameter name if available.
		"""
		self.parname = name

		"""
		'step' - the step size to be used in calculating the numerical
				derivatives.  If set to zero, then the step size is
				computed automatically.  Ignored when AUTODERIVATIVE=0.
		"""
		self.step = 0.0


		"""
		'mpprint' - if set to 1, then the default iterfunct will print the
				   parameter value.  If set to 0, the parameter value
				   will not be printed.  This tag can be used to
				   selectively print only a few parameter values out of
				   many.  Default: 1 (all parameters printed)
		"""
		self.mpprint = True
		
		
		# an attribute to keep track of an uncertainty estimate (currently symmetric)
		self.uncertainty = 0.0
		self.name = self.parname
		
		
		self.independent = False
		
	@property
	def parinfo(self):
		return self.__dict__

	@parinfo.setter
	def parinfo(self, value):
		for key in value.keys():
			self.__dict__[key] = value[key]    
	
	def float(self, value=None, limits=None):
		'''Helper function to cause a parameter to be able to float.'''
		self.fixed = False
		if value is not None:
			self.value = value

		if limits is not None:
			self.limits = limits
			self.limited = [True,True]
			
		shrink = 100.0
		if self.value != 0:
			self.step = np.minimum(np.abs(self.limits[1] - self.limits[0]), self.value/shrink)
		if self.value == 0:
			self.step = np.abs(self.limits[1] - self.limits[0])/shrink
			
			
	def fix(self, value=None):
		'''Helper function to fix a parameter.'''
		self.fixed = True
		if value is not None:
			self.value=value
			
	def __str__(self):
		return "{0:12} = {1}".format(self.name, self.value)
	
	def __float__(self):
		return self.value

