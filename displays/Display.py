'''Tools for displaying 2D/3D datasets.'''

import numpy as np

from ..Talker import Talker


class Display(Talker):
    '''Display 2D or 3D datasets, using a variety of methods.'''
    def __init__(self, **kwargs):
        # decide whether or not this creature is chatty
        Talker.__init__(self, **kwargs)

def logify(im):
    logged = np.log(im)
    logged[np.isfinite(logged) == False] = np.min(logged[np.isfinite(logged)])
    return logged
