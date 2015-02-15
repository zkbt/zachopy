import numpy as np
import matplotlib.pyplot as plt
import astropy.io.ascii
import scipy.interpolate
from zachopy.Talker import Talker

class Relation(Talker):
    '''Base class for astrophysical relations, defining tools to read tables, define methods, etc...'''
    def __init__(self, filename, **kwargs):
        '''Initialize a Relation object.'''

        # decide if it should be chatty
        Talker.__init__(self, **kwargs)

        # store the data filename
        self.filename = filename

        # load the data table
        self.load()


    def load(self):
        self.table = astropy.io.ascii.read(self.filename, fill_values=[('...', np.nan)] )
        self.speak('loaded data from {0}'.format(self.filename))

    @property
    def possible(self):
        return self.table.colnames

    def tofrom(self, outkey, verbose=True):

        # create a function that takes one input as a keyword arg
        def function(inkey):
            return self.interpolator(inkey=inkey, outkey=outkey)


        return function

    def interpolator(self, inkey=None, outkey=None):
        self.speak('creating interpolator to convert {0} to {1}'.format(inkey, outkey))
        try:
            x = self.table[inkey]
        except:
            self.warning("it seems like the attempted input key {0} isn't valid".format(inkey))
            return None
        try:
            y = self.table[outkey]
        except:
            self.warning("it seems like the attempted output key {0} isn't valid".format(outkey))
            return None

        return scipy.interpolate.interp1d(x,y)
