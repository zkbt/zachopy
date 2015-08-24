import matplotlib.pyplot as plt, numpy as np
import scipy.special, scipy.stats, scipy.interpolate

def chi2sigma(v, df):

	# v = the value of chi^2
	# df = the number of degrees of freedom used
	# (note - this probably doesn't make sense to use for things that are below 1 sigma significance - think about it?)

	# create a grid of "sigma" values, over which a Gaussian CDF will be evaluated
	sigma = np.linspace(1, 10, 1000)

	# the p-value associated with the grid of sigmas
	prob = 1.0 - scipy.special.erf(sigma/np.sqrt(2))

	# the p-value associated with the value of chi^2, given the degrees of freedom
	chiprob = 1.0 - scipy.stats.chi2.cdf(v, df)
	print chiprob

	# find the sigma value where these two intersect
	interpolator = scipy.interpolate.interp1d(prob, sigma)
	intersect = interpolator(chiprob)

	# plot the results, just to check
	plt.cla()
	plt.ion()
	plt.plot(sigma, prob)
	plt.title('{0} for {1} dof = {2} sigma'.format(v, df, intersect))
	plt.yscale('log')
	plt.xlabel('sigma')
	plt.ylabel('FAP')

	plt.axvline(intersect)
	plt.axhline(chiprob)

	return intersect
