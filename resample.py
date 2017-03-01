'''Tools for resampling array from grid of independent variables to another.'''

import numpy as np
import scipy.interpolate
import matplotlib.pyplot as plt

def binsizes(x):
	'''If x is an array of bin centers, calculate what their sizes are.
		(assumes outermost bins are same size as their neighbors)'''

	binsize = np.zeros_like(x)
	binsize[0:-1] = (x[1:] - x[0:-1])
	binsize[-1] = binsize[-2]
	return binsize

def plotboxy(x, y, **kwargs):
	'''
	Plot with boxes, to show the left and right edges of a box. This is useful,
	for example, to plot flux associated with pixels, in case you are trying to
	do a sub-pixel resample or interpolation or shift.

	(kwargs are passed on to plt.plot)
	'''

	# what are the edges of the bins (making a guess for those on the ends)
	xbinsize = binsizes(x)
	xleft = x - xbinsize/2.0
	xright = x + xbinsize/2.0

	# create a array that doubles up the y values, and interleaves the edges
	plot_x = np.vstack((xleft,xright)).reshape((-1,),order='F')
	plot_y = np.vstack((y,y)).reshape((-1,),order='F')

	# plot those constructed arrays
	plt.plot(plot_x, plot_y, **kwargs)

def fluxconservingresample(xin, yin, xout, test=False, visualize=False, demo=False):
	'''
	Starting from some initial x and y, resample onto a different grid
	(either higher or lower resolution), while conserving total flux.
	'''

	# what's the cumulative distribution of the yin?
	xinbinsize = binsizes(xin)
	xinleft = xin - xinbinsize/2.0
	xinright = xin + xinbinsize/2.0
	xinforcdf = np.hstack([xinleft, xinright[-1]])
	yinforcdf = np.hstack([0, yin])
	cdfin = np.cumsum(yinforcdf)

	# create an interpolator for that
	cdfinterpolator = scipy.interpolate.interp1d(xinforcdf, cdfin,
						kind='linear',
						bounds_error=False,
						fill_value=(0.0, np.sum(yin)))

	# calculate bin edges (of size len(xout)+1)
	xoutbinsize = binsizes(xout)
	xoutleft = xout - xoutbinsize/2.0
	xoutright = xout + xoutbinsize/2.0
	xoutcdf = np.hstack([xoutleft, xoutright[-1]])
	# interpolate to those bin edges
	cdfout = cdfinterpolator(xoutcdf)
	yout = np.diff(cdfout)

	if visualize:
		fi, (ax_cdf, ax_pdf) = plt.subplots(2,1, sharex=True)
		inkw = dict(color='black', alpha=0.5, linewidth=2, marker='+', markeredgecolor='none')
		outkw = dict(color='orange', alpha=0.5, linewidth=2, marker='.', markeredgecolor='none')


		legkw = dict(fontsize=10, frameon=False, loc='best')

		# plot the PDFs
		plt.sca(ax_pdf)
		plt.ylabel('Flux per (Original) Pixel')

		# plot the original pixels
		plotboxy(xin, yin/xinbinsize,
					label='Original Pixels', **inkw)


		# what would a bad interpolation look like?
		badinterpolation = scipy.interpolate.interp1d(xin, yin/xinbinsize,
							kind='linear',
							bounds_error=False,
							fill_value=0.0)
		plt.plot(xout, badinterpolation(xout),
						color='blue', alpha=0.2, linewidth=1, marker='+',
						label='Silly Simple Interpolation')

		plt.plot(xout, yout/xoutbinsize, label='Flux-Conserved Resample', **outkw)
		plt.legend(**legkw)

		# plot the CDFs
		plt.sca(ax_cdf)
		plt.ylabel('Cumulative Flux (from left)')
		plt.plot(xinforcdf, cdfin,
					label='Original Pixels', **inkw)
		plt.plot(xoutcdf, cdfout,
			label='Flux-Conserved Resample', **outkw)
		plt.legend(**legkw)
		if demo:
			a = raw_input("Pausing a moment to check on interpolation; press return to continue.")

	# return the resampled y-values
	return yout

def testFCR(supersample=True):
	xinitial = np.linspace(1,5,7)
	yinitial = np.random.uniform(0.0, 0.1, len(xinitial))
	if supersample:
		xresample = np.linspace(-1,8,100)
	else:
		xresample = np.linspace(-1,8,5)
	yresample = fluxconservingresample(xinitial, yinitial, xresample, visualize=True)
