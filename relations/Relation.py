import numpy as np
import matplotlib.pyplot as plt
import astropy.io.ascii
import scipy.interpolate
import os
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
        self.table = astropy.io.ascii.read(os.path.dirname(__file__) + '/'+ self.filename, fill_values=[('...', np.nan)] )
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

        return scipy.interpolate.interp1d(x,y, bounds_error=False, fill_value=np.nan)

    def plotone(self, inkey, outkey):
        try:
            self.ax.cla()
        except:
            plt.figure('Relations Possible for '+self.__class__.__name__)
            self.ax = plt.subplot()

        interpolator = self.interpolator(inkey=inkey, outkey=outkey)
        x = np.linspace(np.nanmin(interpolator.x), np.nanmax(interpolator.x), 100)
        self.ax.plot(x, interpolator(x), alpha=0.5, color='sienna')
        self.ax.plot(self.table[inkey], self.table[outkey], marker='o', alpha=0.5, color='black')
        self.ax.set_xlabel(inkey)
        self.ax.set_ylabel(outkey)

    def plot(self):
        plt.figure('Relations Possible for '+self.__class__.__name__, figsize=(len(self.possible)*8, len(self.possible)*8),dpi=30)
        gs = plt.matplotlib.gridspec.GridSpec(len(self.possible), len(self.possible), wspace=0.3, hspace=0.3)
        for i in range(len(self.possible)):
            for j in range(len(self.possible)):
                inkey = self.possible[j]
                outkey = self.possible[i]
                self.ax = plt.subplot(gs[i,j])
                try:
                    self.plotone(inkey, outkey)
                    self.speak('plotted {0} to {1}'.format(inkey, outkey))
                except:
                    self.speak('failed to plot {0} to {1}'.format(inkey, outkey))
            self.speak('{0}/{1}'.format(i+1, len(self.possible)))
        plt.savefig(self.filename + '.pdf')
        plt.draw()
