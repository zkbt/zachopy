'''Tools for displaying 2D/3D datasets.'''

from matplotlib import pyplot as plt, numpy as np
import glob, os
import astropy.io.fits
import zachopy.utils
from zachopy.Talker import Talker

class Display(Talker):
    '''Display 2D or 3D datasets, using a variety of methods.'''
    def __init__(self, **kwargs):
        # decide whether or not this creature is chatty
        Talker.__init__(self)
