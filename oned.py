'''Tools for dealing with 1D arrays, particularly timeseries and spectra.'''
import matplotlib.pyplot as plt
import numpy as np
np.seterr(divide='ignore')
import astropy.modeling.models, astropy.modeling.fitting
import scipy.interpolate, scipy.stats

def mad(x):
	'''
		Returns the median absolute deviation from the median,
			a robust estimator of a distribution's width.

			For a Gaussian distribution, sigma~1.48*MAD.
	'''
	med = np.median(x)
	return np.median(np.abs(x - med))

def binto(x=None, y=None, yuncertainty=None,
			binwidth=0.01,
			test=False,
			robust=True,
			sem=True,
			verbose=False):
	'''Bin a timeseries to a given binwidth,
		returning both the mean and standard deviation
			(or median and approximate robust scatter).'''

	if test:
		n = 1000
		x, y = np.arange(n), np.random.randn(n) - np.arange(n)*0.01 + 5
		bx, by, be = binto(x, y, binwidth=20)
		plt.figure('test of zachopy.binto')
		plt.cla()
		plt.plot(x, y, linewidth=0, markersize=4, alpha=0.3, marker='.', color='gray')
		plt.errorbar(bx, by, be, linewidth=0, elinewidth=2, capthick=2, markersize=10, alpha=0.5, marker='.', color='blue')
		return

	min, max = np.min(x), np.max(x)
	bins = np.arange(min, max+binwidth, binwidth)
	count, edges = np.histogram(x, bins=bins)
	sum, edges = np.histogram(x, bins=bins, weights=y)

	if yuncertainty is not None:
		count, edges = np.histogram(x, bins=bins)
		numerator, edges = np.histogram(x, bins=bins, weights=y/yuncertainty**2)
		denominator, edges = np.histogram(x, bins=bins, weights=1.0/yuncertainty**2)
		mean = numerator/denominator
		std = np.sqrt(1.0/denominator)
		error = std
		if False:
			for i in range(len(bins)-1):
				print bins[i], mean[i], error[i], count[i]
			a = raw_input('???')
	else:
		if robust:
			n= len(sum)
			mean, std = np.zeros(n) + np.nan, np.zeros(n) + np.nan
			for i in range(n):
				inbin = (x>edges[i])*(x<=edges[i+1])
				mean[i] = np.median(y[inbin])
				std[i] = 1.48*mad(y[inbin])
		else:
			if yuncertainty is None:
				mean = sum.astype(np.float)/count
				sumofsquares, edges = np.histogram(x, bins=bins, weights=y**2)
				std = np.sqrt(sumofsquares.astype(np.float)/count - mean**2)*np.sqrt(count.astype(np.float)/np.maximum(count-1.0, 1.0))
		if sem:
			error = std/np.sqrt(count)
		else:
			error = std


	x = 0.5*(edges[1:] + edges[:-1])
	return x, mean, error

	if yuncertainty is not None:
		print "Uh-oh, the yuncertainty feature hasn't be finished yet."

	if robust:
		print "Hmmm...the robust binning feature isn't finished yet."

def mediansmooth(x, y, xsmooth=0):
	'''
		smooth a (not necessarily evenly sampled) timeseries

			x = the independent variable
			y = the dependent variable
			xsmooth = the *half-width* of the smoothing box
	'''
	assert(x.shape == y.shape)
	ysmoothed = np.zeros_like(x)
	for i, center in enumerate(x):
		relevant = np.abs(x - center) <= xsmooth
		ysmoothed[i] = np.median(y[relevant])
	return ysmoothed

def peaks(	x, y,
			plot=False,
			xsmooth=30,
			threshold=100,
			edgebuffer=10,
			maskwidth=10):
	'''Return the significant peaks in a 1D array.

			peaks(x, y, plot=False, threshold=4, maskwidth=10)

			required:
				x, y = two 1D arrays
			optional:
				plot			# should we show a plot?
				xsmooth			# half-width for median smoothing
				threshold		# peaks above mad selected
				maskwidth   	# when one peak is found, how wide of area is masked around it?
	'''

	# calculate a smoothed version of the curve
	smoothed = mediansmooth(x, y, xsmooth=xsmooth)
	filtered = y - smoothed

	# calculate the mad of the whole thing
	mad = np.median(np.abs(filtered))
	cutoff = mad*threshold

	# create empty lists of peaks
	xPeaks, yPeaks = [],[]

	# keep track of a mask of things that aren't too close to other peaks
	mask = np.ones_like(x)

	# calculate the derivatives
	derivatives = (filtered[1:] - filtered[:-1])/(x[1:] - x[:-1])

	# estimate peaks as zero crossings
	guesses = np.zeros_like(x).astype(np.bool)
	guesses[1:-1] = (derivatives[:-1] > 0) * (derivatives[1:] <= 0)

	# make sue the peak is high enough to be interesting
 	guesses *= filtered > cutoff

	# make sure the peak isn't too close to an edge
	guesses *= (x > np.min(x) + edgebuffer)*(x < np.max(x) - edgebuffer)

	if plot:
		# turn on interactive plotting
		plt.ion()

		# create a figure and gridspec
		fi = plt.figure('peak finding')
		gs = plt.matplotlib.gridspec.GridSpec(2,1, hspace=0.03)

		# create axes for two kinds of plots
		ax_raw = plt.subplot(gs[0])
		plt.setp(ax_raw.get_xticklabels(), visible=False)
		ax_filtered = plt.subplot(gs[1], sharex=ax_raw)

		# plot the input vector
		kw = dict(alpha=1, color='gray', linewidth=1)
		ax_raw.plot(x, y, **kw)
		ax_filtered.plot(x, filtered, **kw)

		# plot the threshold
		kw = dict(alpha=0.5, color='royalblue', linewidth=1)
		ax_raw.plot(x, cutoff + smoothed, **kw)
		ax_filtered.plot(x, cutoff + np.zeros_like(x), **kw)

		# set the scale
		ax_raw.set_yscale('log')
		ax_filtered.set_yscale('log')
		ax_filtered.set_ylim(mad, np.max(filtered))

		kw = dict(marker='o', color='none', markeredgecolor='tomato', alpha=1, markersize=10)
		ax_raw.plot(x[guesses], y[guesses], **kw)
		ax_filtered.plot(x[guesses], filtered[guesses], **kw)

		plt.draw()
		a = raw_input("how 'bout them peaks?")

	return x[guesses], y[guesses]

	'''a = raw_input('?')
	# start at the highest point
	highest = np.nonzero(filtered*mask == np.nanmax(filtered*mask))[0]

	highest = np.where(y*mask == np.nanmax((y*mask)))[0]


	highest = highest[0]
	#print highest, highest.shape
	while (y*mask)[highest] > threshold*mad:
		g1 = astropy.modeling.models.Gaussian1D(amplitude=y[highest], mean=x[highest], stddev=1.0)
		xtomask = (g1.mean + np.arange(-g1.stddev.value*maskwidth, g1.stddev.value*maskwidth))
		toMask = np.interp(xtomask, x, np.arange(len(x))).astype(int)
		toMask = toMask[toMask < len(x)]
		toMask = toMask[toMask >= 0]

		if len(toMask) > 0:
			gfitter = astropy.modeling.fitting.LevMarLSQFitter()
			fit = gfitter(g1, x[toMask], y[toMask])
			#print g1
			if g1.stddev.value < 5:
				xPeaks.append(fit.mean.value)
				yPeaks.append(fit.amplitude.value)
				if plot:
					ax[0].plot(x[toMask], g1(x[toMask]))
					ax[1].plot(x[toMask], g1(x[toMask]))

		mask[toMask] = 0.0
		highest = np.where(y*mask == np.nanmax(y*mask))[0]
		highest=highest[0]


	if plot:
		ax[0].scatter(xPeaks, yPeaks)
		ax[1].scatter(xPeaks, yPeaks)

	a = raw_input('what do you think of this peakfinding?')
	return np.array(xPeaks), np.array(yPeaks)'''

def subtractContinuum(s, n=3):
	'''Take a 1D array, use spline to subtract off continuum.

			subtractContinuum(s, n=3)

			required:
			s = the array

			optional:
			n = 3, the number of spline points to use
	'''

	x = np.arange(len(s))
	points = (np.arange(n)+1)*len(s)/(n+1)
	spline = scipy.interpolate.LSQUnivariateSpline(x,s,points)
	#plt.ion()
	#plt.figure()
	#plt.plot(x, s1)
	#plt.plot(x, spline(x), linewidth=5, alpha=0.5)
	return s - spline(x)

def binsizes(x):
	binsize = np.zeros_like(x)
	binsize[0:-1] = (x[1:] - x[0:-1])
	binsize[-1] = binsize[-2]
	return binsize

def supersample(xin=None, yin=None, xout=None, demo=False, visualize=False, slow=True):
	'''Super-sample an array onto a denser array, using nearest neighbor interpolation, handling edges of pixels properly.
		(should be flux-preserving)
			xin = input array of coordinates
			yin = input array of values
			xout = output array of coordinates where you would like values.
		| xin[1:] - x[0:-1] must always be bigger than the largest spacing of the supersampled array |
		| assumes coordinates are the center edge of bins, for both xin and xout |'''
	# maybe I could make this faster using np.histogram?

	if demo:
		visualize=True
		n = 10
		xin = np.arange(n)
		yin = np.random.random(n) + xin
		nout = (20+ np.random.random())*n
		xout = np.linspace(xin.min()-2, xin.max()+2, nout)

	assert(xin is not None)
	assert(yin is not None)
	assert(xout is not None)

	xinbinsize = binsizes(xin)
	xinleft = xin - xinbinsize/2.0
	xinright = xin +xinbinsize/2.0

	xoutbinsize = binsizes(xout)
	xoutleft = xout - xoutbinsize/2.0
	xoutright = xout + xoutbinsize/2.0

	if slow:
		yout = np.zeros_like(xout).astype(np.float)
		for out in range(len(xout)):
			try:
				inleft = (xinleft <= xoutleft[out]).nonzero()[0].max()
			except:
				inleft = 0

			try:
				inright = (xinright >= xoutright[out]).nonzero()[0].min()
			except:
				inright = -1

			leftweight = (np.minimum(xinright[inleft], xoutright[out]) - xoutleft[out])/(xinright[inleft] - xinleft[inleft])
			rightweight = (xoutright[out] - np.maximum(xinleft[inright],xoutleft[out]))/(xinright[inright] - xinleft[inright])*(inright != inleft)

			yout[out] = (leftweight*yin[inleft] + rightweight*yin[inright])/(leftweight + rightweight)
			#if renormalize:
			#	yout[out] *= (0.5*xinbinsize[inleft] + 0.5*xinbinsize[inright])/xoutbinsize[out]
			#print "{0:4f} to {1:4f} = {2:6f}x{3:6f} + {4:6f}x{5:6f}".format(xoutleft[out], xoutright[out], leftweight, xin[inleft], rightweight, xin[inright])
		yout[xoutright > xinright.max()] = 0
		yout[xoutleft < xinleft.min()] = 0
	else:

		ones = np.ones((len(xin), len(xout)))

		# set up the input arrays
		sh = (len(xin),1)
		matrix_xinleft = ones*xinleft.reshape(sh)
		matrix_xinright = ones*xinright.reshape(sh)
		matrix_xinbinsize = ones*xinbinsize.reshape(sh)
		matrix_yin = ones*yin.reshape(sh)

		# set up temporary output arrays
		matrix_xoutleft = xoutleft*ones
		matrix_xoutright = xoutright*ones

		mask_left = (matrix_xinleft <= matrix_xoutleft) & (matrix_xinleft + matrix_xinbinsize >= matrix_xoutleft)
		mask_right = (matrix_xinleft <= matrix_xoutright) & (matrix_xinleft + matrix_xinbinsize >= matrix_xoutright)

		leftweight = (np.minimum(matrix_xinright, matrix_xoutright) - matrix_xoutleft)/matrix_xinbinsize*mask_left
		rightweight = (matrix_xoutright - np.maximum(matrix_xinleft,matrix_xoutleft))/matrix_xinbinsize*mask_right
		yout = np.sum((leftweight*matrix_yin+ rightweight*matrix_yin),0)/np.sum(leftweight + rightweight,0)



	'''ones = np.ones((len(xin), len(xout)))
	matrix_xout = xout*ones
	matrix_xoutbin = binsizes(xout)*ones


	matrix_yin = ones*yin.reshape((len(xin),1))
	matrix_left = ones*xinleft.reshape((len(xin),1))
	matrix_right = ones*xinright.reshape((len(xin),1))

	rightweight = (matrix_right - matrix_xout)/matrix_xoutbin
	rightweight *= (matrix_right - matrix_xout < 1) * (matrix_xout - matrix_left >= 0)
	print rightweight
	print
	leftweight = (matrix_xout - matrix_left)/matrix_xoutbin
	leftweight *= (matrix_right - matrix_xout< 1) * (matrix_xout - matrix_left >= 0)
	print leftweight
	print
	print leftweight + rightweight

	#matrix_yout = matrix_yin[0:-1,:]*rightweight[0:-1,:] + matrix_yin[1:None,:]*leftweight[0:-1,:]

	matrix_yout = matrix_yin[0:-1,:]*leftweight[0:-1,:] + matrix_yin[1:None,:]*rightweight[1:None,:]'''
	#yout = np.sum(matrix_yout, 0)

	if visualize:
		plt.cla()
		plot_xin = np.vstack((xinleft,xinright)).reshape((-1,),order='F')
		plot_yin = np.vstack((yin,yin)).reshape((-1,),order='F')
		plt.plot(plot_xin, plot_yin, alpha=0.5, linewidth=3, color='black')
		badinterpolation = scipy.interpolate.interp1d(xin, yin, kind='linear', bounds_error=False, fill_value=0.0)
		plt.plot(xout, badinterpolation(xout), color='red', alpha=0.2, linewidth=2)

		plot_xout = np.vstack((xoutleft,xoutright)).reshape((-1,),order='F')
		plot_yout = np.vstack((yout,yout)).reshape((-1,),order='F')
		plt.plot(plot_xout, plot_yout, color='orange', alpha=0.7, linewidth=4, markersize=10)
		plt.plot(xout, yout, color='orange', alpha=0.7, linewidth=0, markersize=20)
		a = raw_input('okay?')
	return yout

def plothistogram( y, nbins=None, binwidth=0.1, ax=plt.gca(), expectation=None, scale='linear', nsigma=5, **kwargs):

	if nbins is not None:
		binwidth = (np.max(y) - np.min(y))/nbins


	if expectation is not None:
		mean = expectation[0]
		width = expectation[1]
		min = mean - nsigma*width
		max = mean + nsigma*width
	else:
		pad = 3
		min = np.min(y)-pad*binwidth
		max = np.max(y)+pad*binwidth

	yhist, edges = np.histogram(y, bins=np.arange(min, max, binwidth))
	if len(edges) == 1:
		return
	if np.max(yhist) == 0:
		return
	normalization = (len(y)+0.0)/nsigma
	yhist = np.array(yhist).astype(float)/ normalization
	xhist = (edges[1:] + edges[0:-1])/2.0
	# if given an expectation, plot it as a histogram
	if expectation is not None:
		g = scipy.stats.norm(mean, width)
		n = len(y)
		exhist = np.zeros(len(xhist))
		for i in range(len(xhist)):
			start = xhist[i] - binwidth/2.0
			finish = xhist[i] + binwidth/2.0
			exhist[i] = n*(g.cdf(finish) - g.cdf(start))
		bottom = np.maximum(exhist - np.sqrt(exhist), 0)/normalization
		top = (exhist + np.sqrt(exhist))/normalization

		ax.fill_betweenx(xhist, bottom, top, color='gray', alpha=0.5, linewidth=4)
		ax.plot(top, xhist, color='gray', alpha=0.5, linewidth=4)

	ax.plot(np.maximum(yhist, 0.000001/normalization), xhist,  **kwargs)
	if scale == 'log':
		ax.set_xscale('log')
		ax.set_xlim(0.9/normalization,  np.max(exhist/normalization)*1.3)
	if scale == 'linear':
		ax.set_xscale('linear')
		ax.set_xlim(0, np.max(exhist/normalization)*1.3)

	#ax.set_ylim(min, max)
	#ax.set_xticks([])
	#ax.set_yticks([])
	#print "HISTOGRAMMING!"
	#print xhist
	#print yhist
	#print exhist/normalization
	#assert(False)

def binnedrms(y):
	# define a dummy x variable
	x = np.arange(len(y))

	n = np.arange(1,len(y)/3)
	rms = np.zeros(len(n))
	for i in range(len(n)):
		binned = np.histogram(x, bins=np.arange(len(x)/n[i])*n[i], weights=y)[0]/n[i]
		#print binned
		rms[i] = np.std(binned)
		#print n[i], rms[i]
	return n, rms

def plotbinnedrms(y, ax=plt.gca(), xunit=1, scale='log', yunits=1, yrange=[50,5000], updateifpossible=True, **kwargs):
	n, rms = binnedrms(y*yunits)
	x = xunit*n

	# if the plot is already full,
	try:
		assert(updateifpossible)
		lines = ax.get_lines()
		lines[0].set_data(x, rms[0]/np.sqrt(n))
		lines[1].set_data(x, rms)
	except:
		ax.plot(x, rms[0]/np.sqrt(n), linestyle='--', color='black', alpha=0.25, linewidth=3)
		ax.plot(x, rms, **kwargs)

	if scale == 'log':
		ax.set_xscale('log')
		ax.set_yscale('log')
		ax.set_ylim(*yrange)
		ax.set_xlim(1, np.max(n))
	else:
		ax.set_xlim(0, np.max(x)+1)
		ax.set_ylim(0, np.max(yrange))

def acf(y):
	a = np.correlate(y,y,'full')
	trimmed = a[len(a)/2:]
	lag = np.arange(len(trimmed))
	return lag, trimmed/np.correlate(y,y)


def plotautocorrelation(y, xunit=1, ax= plt.gca(), max=25,  yrange=[-0.2, 1], **kwargs):
	lag, auto = acf(y)
	x = lag*xunit
	end = np.minimum(len(y), max)
	#try:
	#	lines = ax.get_lines()
	#	lines[1].set_data
	#except:
	#	pass
	ax.plot([0, end -1], [0,0], linestyle='--', color='black', alpha=0.25, linewidth=3)
	ax.plot(x, auto, **kwargs)
	ax.set_xlim(-1, end)
	ax.set_ylim(*yrange)

def ccf(f, g, scale=1.0):
	'''Calculate the normalized cross-correlation function of two identically-size arrays.

		[required]:
		f = an N-element array (for example, spectrum of target star)
		g = an N-element array (for example, spectrum of template star)
		scale = a scalar indicating what the indices of f and g (one unit of "lag") correspond to

		'''

	# how long are our arrays
	N = len(f)

	# define the x-axis, if not supplied
	assert(len(f) == len(g))
	x = np.arange(-N+1, N, 1.0)*scale

	# calculation the normalized cross-correlation function
	sigma_f = np.sqrt(np.sum(f**2)/N)
	sigma_g = np.sqrt(np.sum(g**2)/N)
	C_fg = np.correlate(f, g, 'full')/N/sigma_f/sigma_g

	# WILL THIS WORK?
	return scipy.interpolate.interp1d(x,C_fg, fill_value=0.0, bounds_error=False)

def todcor(f, g1, g2, scale=1.0, luminosity_ratio=None):
	'''Calculate the 2D correlation of a 1D array with two template arrays.'''

	assert(len(f) == len(g1))
	assert(len(f) == len(g2))

	C_1 = ccf(f, g1, scale=scale)
	C_2 = ccf(f, g2, scale=scale)
	C_12 = ccf(g1, g2, scale=scale)

	N = len(f)
	sigma_g1 = np.sqrt(np.sum(g1**2)/N)
	sigma_g2 = np.sqrt(np.sum(g2**2)/N)

	def bestalphaprime(s1, s2):
		return sigma_g1/sigma_g2*(C_1(s1)*C_12(s2 - s1) - C_2(s2))/(C_2(s2)*C_12(s2-s1) - C_1(s1))

	def R(s1, s2):
		#a =
		if luminosity_ratio is None:
			a = np.maximum(np.minimum(bestalphaprime(s1,s2), sigma_g2/sigma_g1), 0.0)
			flexiblecorrelation = (C_1(s1) + a*C_2(s2))/np.sqrt(1.0 + 2*a*C_12(s2 - s1) + a**2)
			ok = np.isfinite(a)
			peak = np.argmax(flexiblecorrelation[ok].flatten())
			a = a[ok].flatten()[peak]
		else:
			a = luminosity_ratio*sigma_g2/sigma_g1
		print "alpha spans", np.min(a), np.max(a)
		return  (C_1(s1) + a*C_2(s2))/np.sqrt(1.0 + 2*a*C_12(s2 - s1) + a**2), a*sigma_g1/sigma_g2

	return R
