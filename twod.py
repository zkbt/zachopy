'''Tools for dealing with 1D arrays, particularly timeseries of images.'''
import numpy as np
import scipy.ndimage
import matplotlib.pyplot as plt
import displays.ds9

def scatter(cube, axis=0):
    shape = np.array(cube.shape)
    shape[axis] = 1

    med = np.median(cube, axis=axis)
    mad = np.median(np.abs(cube - med.reshape(shape)), axis=axis)
    return 1.48*mad


def stack(cube, axis=0, threshold=5.0):
    '''Combine a cube of images into one mean image, using a MAD noise estimator to reject outliers.'''
    shape = np.array(cube.shape)
    shape[axis] = 1

    med = np.median(cube, axis=axis).reshape(shape)
    noise = scatter(cube, axis=axis).reshape(shape)
    good = (np.abs(cube - med) < threshold*noise) | (noise == 0)
    mean = np.sum(good*cube, axis=axis)/np.sum(good, axis=axis)

    return mean, noise#.squeeze()

def interpolateOverBadPixels(image, bad, scale=2, visualize=False):
    '''Take an image and a bad pixel mask (=1 where bad, =0 otherwise) and interpolate over the bad pixels, using a Gaussian smoothing.'''
    smoothed = scipy.ndimage.filters.gaussian_filter(image*(bad == False), sigma=[scale,scale])
    weights = scipy.ndimage.filters.gaussian_filter(np.array(bad == False).astype(np.float), sigma=[scale,scale])
    smoothed /=weights
    corrected = image + 0.0
    corrected[bad.astype(np.bool)] = smoothed[bad.astype(np.bool)]
    if visualize:
        gs = plt.matplotlib.gridspec.GridSpec(1,4, wspace=0,hspace=0)
        orig = plt.subplot(gs[0])
        smoo = plt.subplot(gs[1], sharex=orig, sharey=orig)
        weig = plt.subplot(gs[2], sharex=orig, sharey=orig)
        corr = plt.subplot(gs[3], sharex=orig, sharey=orig)
        kw = dict(cmap='gray', interpolation='nearest')
        orig.imshow(np.log(image), **kw)
        smoo.imshow(np.log(smoothed), **kw)
        weig.imshow(bad, **kw)
        corr.imshow(np.log(corrected), **kw)
        plt.draw()
        a = raw_input('test?')
    return corrected


def polyInterpolate(image, bad, axis=0, order=2, visualize=True):
    '''Take an image and a bad pixel mask (=1 where bad, =0 otherwise), fit polynomials to the good data in one dimension, and return this polynomial smoothed version.'''
    n = image.shape[axis]
    smoothed = np.zeros_like(image)
    if visualize:
        plt.figure('interpolating in a 2D image')
        gs = plt.matplotlib.gridspec.GridSpec(1,1)
        ax = plt.subplot(gs[0,0])
        d = displays.ds9('poly')

    for i in range(image.shape[axis]):
        ydata = image.take(i, axis=axis)
        baddata = bad.take(i, axis=axis)
        xdata = np.arange(len(ydata))
        ok = baddata == 0
        med = np.median(ydata[ok])
        mad = np.median(np.abs(ydata[ok] - med))
        ok = ok*(np.abs(ydata - med) < 4*1.48*mad)


        fit = np.polynomial.polynomial.polyfit(xdata[ok], ydata[ok], order)
        poly = np.polynomial.polynomial.Polynomial(fit)

        if visualize:
            ax.cla()
            ax.plot(xdata, ydata, alpha=0.3, color='gray', marker='o')
            ax.plot(xdata[ok], ydata[ok], alpha=1, color='black', marker='o', linewidth=0)
            ax.plot(xdata, poly(xdata), alpha=0.3, color='red', linewidth=5)
            ax.set_ylim(0, np.percentile(image[bad == 0], 95))
            plt.draw()

        if axis == 0:
            smoothed[i,:] =  poly(xdata)
        else:
            smoothed[:,i] = poly(xdata)

    if visualize:
        d.update(smoothed)
    return smoothed
        #a = raw_input('?')
    '''smoothed = scipy.ndimage.filters.gaussian_filter(image*(bad == False), sigma=[scale,scale])
    weights = scipy.ndimage.filters.gaussian_filter(np.array(bad == False).astype(np.float), sigma=[scale,scale])
    smoothed /=weights
    corrected = image + 0.0
    corrected[bad.astype(np.bool)] = smoothed[bad.astype(np.bool)]
    if visualize:
        gs = plt.matplotlib.gridspec.GridSpec(1,4, wspace=0,hspace=0)
        orig = plt.subplot(gs[0])
        smoo = plt.subplot(gs[1], sharex=orig, sharey=orig)
        weig = plt.subplot(gs[2], sharex=orig, sharey=orig)
        corr = plt.subplot(gs[3], sharex=orig, sharey=orig)
        kw = dict(cmap='gray', interpolation='nearest')
        orig.imshow(np.log(image), **kw)
        smoo.imshow(np.log(smoothed), **kw)
        weig.imshow(bad, **kw)
        corr.imshow(np.log(corrected), **kw)
        plt.draw()
        a = raw_input('test?')
    return corrected'''

def estimateBackground(image, axis=-1):

    display = displays.ds9('background subtraction')
    display.one(image, clobber=True)

    roughSky1d = np.median(image, axis)
    shape = np.array(image.shape)
    shape[axis] = 1
    roughSkyImage = np.ones_like(image)*roughSky1d.reshape(shape)
    display.one(roughSkyImage)
    display.one(image - roughSkyImage)
    assert(False)
