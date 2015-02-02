'''Keep track of a multidimensional PDF.'''
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec
from transit.Parameter import Parameter

class PDF(object):
	def __init__(self, parameters=None, covariance=None, samples=None):
		'''Initialize a PDF, using either parameters and covariance, or samples'''

		# initialize the parameters
		if parameters is None:
			#figure out parameter names and values from samples
			self.parameters = []
			for key in samples.keys():
				self.parameters.append(Parameter(key,np.mean(samples[key])))
		else:
			self.parameters=parameters
		self.n = len(self.parameters)

		# initialize the covariance
		if covariance is None:
			# figure out covariance from samples
			self.covariance = np.zeros((self.n, self.n))
			for i in range(self.n):
				for j in range(self.n):
					dx = samples[self.parameters[i].name][:] - self.parameters[i].value
					dy = samples[self.parameters[j].name][:] - self.parameters[j].value
					self.covariance[i,j] = np.mean(dx*dy)
		else:
			self.covariance = covariance

		if samples is None:
			# simulate some samples from the parameter values and the covariance matrix
			self.simulateSamples()
			for i in range(self.n):
				self.parameters[i].uncertainty = np.sqrt(self.covariance[i,i])
		else:
			self.samples = samples
			for i in range(self.n):
				self.parameters[i].uncertainty = np.std(self.samples[self.parameters[i].name])

		# make a few arrays to make things more convenient
		self.names = [parameter.name for parameter in self.parameters]
		self.values = [parameter.value for parameter in self.parameters]

		self.color_samples = 'Black'
		self.color_gauss = 'SeaGreen'

	def simulateSamples(self, n=100):
		'''Use parameter values and covariances to generate samples
				(requires that these are both defined ahead of time.)'''
		parameters = self.parameters
		covariance = self.covariance
		means = [parameter.value for parameter in parameters]

		s = np.random.multivariate_normal(means, covariance, n)
		self.samples = {}
		for i in range(len(parameters)):
			self.samples[parameters[i].name] = s[:,i]

	def plot(self, keys=None, plotcovariance=False, onesigmalabels=False, subsample=10000, nbins=100, dye=None):
		'''Make a matrix plot of the PDF.'''

		self.plotcovariance = plotcovariance
		self.onesigmalabels = onesigmalabels
		self.subsample = subsample
		self.dye=dye

		# decide which elements to plot
		if keys is None:
			keys = self.names

		# set up the grid of subplots
		n = len(keys)
		self.figure = plt.figure('matrix')
		gs = matplotlib.gridspec.GridSpec(n,n, hspace=0.05, wspace=0.05)
		self.pdfax = {}

		# loop over columns of the grid (i)
		for i in range(n):
			self.pdfax[keys[i]] = {}
			# loop over rows in the columns (j)
			for j in range(n):
				try:
					self.pdfax[keys[i]][keys[j]].cla()
				except:
					pass
				# setup axis sharing, always share the x axes
				try:
					assert(i != j)
					assert(i != (j-1))
					sharex = self.pdfax[keys[i]][keys[j-1]]
				except:
					sharex = None
				# don't share y axis with the histograms
				try:
					assert(i != j)
					assert((i-1) != j)
					sharey = self.pdfax[keys[i-1]][keys[j]]
				except:
					sharey = None

				# make a plot if in the lower left of the grid
				if i <= j:

					# create (and store) this subplot window
					ax = plt.subplot(gs[j,i], sharex=sharex, sharey=sharey)
					self.pdfax[keys[i]][keys[j]] = ax

					# set the axis labels, along the outside of the plot
					if i > 0:
						plt.setp(ax.get_yticklabels(), visible=False)
					else:
						ax.set_ylabel(keys[j])
					if j < (n-1):
						plt.setp(ax.get_xticklabels(), visible=False)
					else:
						ax.set_xlabel(keys[i])
						plt.sca(ax)
						locs, labels = plt.xticks()
						plt.setp(labels, rotation=90)

					# populate the subplots with data
					if i != j:
						self.plotpair(keys[i], keys[j])
					if i == j:
						self.plothist(keys[i], nbins=nbins)

					if self.onesigmalabels:
						self.fix_ticks('x',keys[i])
						if i != j:
							self.fix_ticks('y',keys[j])
			plt.subplots_adjust(left=0.2, right=0.9, top=0.9, bottom=0.2)
	def fix_ticks(self, which, key, nsigma=2):
		'''Replace the nasty overlapping ticks with angles ones at +/- 2 sigma.'''

		# basics
		i = self.names.index(key)
		ax = plt.gca()

		# position ticks at -nsigma, mean, +nsigma
		ticks = [self.parameters[i].value - self.parameters[i].uncertainty*nsigma, self.parameters[i].value, self.parameters[i].value + self.parameters[i].uncertainty*nsigma]

		# format the tick labels
		def postdecimal(str):
			'''a helper function to figure out how many digits after the decimal point a string contains.'''
			return len(str.split('.')[-1])

		# keep two significant digits on the uncertainties
		uformat = '{0:+.2g}'.format

		# keep the same number of (total) digits for the central value
		vformatstring = '{0}'.format(postdecimal(uformat(self.parameters[i].uncertainty)))
		vformat = ('{0:.'+vformatstring+'f}').format

		# format the text for ticks at -nsigma, mean, +nsigma
		ticklabels = [uformat(-self.parameters[i].uncertainty*nsigma), vformat(self.parameters[i].value), uformat(self.parameters[i].uncertainty*nsigma)]

		# apply the ticks to the correct axis
		if which == 'x':
			lines = ax.set_xticks(ticks)
			labels = ax.set_xticklabels(ticklabels, rotation=45)
			ax.set_xlim(self.parameters[i].value - self.parameters[i].uncertainty*nsigma*2, self.parameters[i].value + self.parameters[i].uncertainty*nsigma*2)
		if which == 'y':
			lines = ax.set_yticks(ticks)
			labels = ax.set_yticklabels(ticklabels, rotation=45)
			ax.set_ylim(self.parameters[i].value - self.parameters[i].uncertainty*nsigma*2, self.parameters[i].value + self.parameters[i].uncertainty*nsigma*2)

		# nudge the tick label sizes
		labels[0].set_size('small')
		labels[1].set_weight('extra bold')
		labels[-1].set_size('small')

	def plothist(self, key, nbins=100):

		# get the plot to populate
		ax = self.pdfax[key][key]

		# plot the histogram of the samples
		ax.hist(self.samples[key], bins=nbins, linewidth=0, alpha=0.5, color=self.color_samples, normed=True)

		# plot the Gaussian approximation
		if self.plotcovariance:
			x = np.linspace(ax.get_xlim()[0], ax.get_xlim()[1], 100)
			i = self.names.index(key)
			mean = self.parameters[i].value
			sigma = self.parameters[i].uncertainty
			plt.plot(x, 1.0/np.sqrt(2*np.pi)/sigma*np.exp(-0.5*(x-mean)**2/sigma**2), color=self.color_gauss, alpha=0.6, linewidth=3)

	def plotpair(self, keyx, keyy):

		stride = np.maximum(len(self.samples[keyx])/self.subsample, 1)
		theta = np.linspace(0, 2*np.pi, 100)

		i = self.names.index(keyx)
		j = self.names.index(keyy)


		ax = self.pdfax[keyx][keyy]
		ax.plot(self.samples[keyx][::stride], self.samples[keyy][::stride],  marker='o', alpha=0.1, linewidth=0, color=self.color_samples)
		nsigma = 2

		if self.plotcovariance:
			bigcovar = self.covariance
			covar = bigcovar[[i,j],:][:,[i,j]]
			cholesky = np.linalg.cholesky(covar)
			theta = np.linspace(0, 2*np.pi, 100)
			x_ellipse, y_ellipse = cholesky.dot(np.array([np.sin(theta), np.cos(theta)]))
			for nsigma in [1,2]:
				kw = {"color":self.color_gauss, 'linewidth':5-nsigma*1, 'alpha':0.8 - 0.2*nsigma}
				plt.plot(nsigma*x_ellipse + self.parameters[i].value, nsigma*y_ellipse + self.parameters[j].value, **kw)
