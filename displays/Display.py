'''Tools for displaying 2D/3D datasets.'''

import numpy as np
from ..Talker import Talker

class Display(Talker):
    '''Display 2D or 3D datasets, using a variety of methods.'''
    def __init__(self, **kwargs):
        # decide whether or not this creature is chatty
        Talker.__init__(self)


def createTestImage(xsize=500, ysize=250):
    '''
    Create a fake image of stars.
    '''

    # create images of x, y, and an empty one to fill with stars
    x1d = np.arange(0, xsize)
    y1d = np.arange(0, ysize)
    x, y = np.meshgrid(x1d, y1d)
    stars = np.zeros_like(x)

    # create N random position for stars
    N = 300
    sx = np.random.uniform(0, xsize, N)
    sy = np.random.uniform(0, ysize, N)

    # set some background level
    bg = 100

    # create a semi-reasonable magnitude distribution for stars
    sf = 10000*10**(-0.4*np.random.triangular(0, 10, 10, N))

    # define the PSF for the stars
    sigma = 2.0
    def gauss(x, y, x0, y0):
        return np.exp(-0.5*((x-x0)**2 + (y-y0)**2)/sigma**2)

    # create a cube with an image for each star, and sum them together into one image
    stars = (sf*gauss(x[:,:,np.newaxis], y[:,:,np.newaxis], x0=sx, y0=sy)).sum(2)

    # create a model images
    model = bg + stars

    # add some noise to it
    image = np.random.normal(model, np.sqrt(model))

    return image
