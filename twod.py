'''Tools for dealing with 1D arrays, particularly timeseries of images.'''
import numpy as np
import scipy.ndimage
import matplotlib.pyplot as plt
import zachopy.display

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

def estimateBackground(image, axis=-1):

    display = zachopy.display.ds9('background subtraction')
    display.one(image, clobber=True)

    roughSky1d = np.median(image, axis)
    shape = np.array(image.shape)
    shape[axis] = 1
    roughSkyImage = np.ones_like(image)*roughSky1d.reshape(shape)
    display.one(roughSkyImage)
    display.one(image - roughSkyImage)
    assert(False)
