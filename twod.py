'''Tools for dealing with 1D arrays, particularly timeseries of images.'''
import numpy as np

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
    good = np.abs(cube - med) < threshold*noise
    return np.sum(good*cube, axis=axis)/np.sum(good, axis=axis)
