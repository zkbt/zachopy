from zachopy.Talker import Talker
import matplotlib.pyplot as plt
import numpy as np
import astropy.table, astropy.io.ascii
import zachopy.display
import python.origami

class Folder(Talker):
    def __init__(self):

        Talker.__init__(self)
        self.period_max = 20.0
        self.read()
        self.gridify()

    def read(self, filename='/Users/zkbt/Desktop/mo23584285-6245423_marples.txt'):
        self.speak('loading text MarPLEs from {0}'.format(filename))
        data = np.loadtxt(filename)
        self.ndurations = (data.shape[1]-1)/2
        min_duration, max_duration = 0.02, 0.1
        durations = np.linspace(min_duration, max_duration, 9)
        assert(len(durations) == self.ndurations)

        self.hjd = data[:,0]
        depths, uncertainties = data[:,1::2].transpose(), data[:,2::2].transpose()
        self.depths = np.ma.MaskedArray(data=depths, mask=uncertainties <= 0)
        self.uncertainties = np.ma.MaskedArray(data=uncertainties, mask=uncertainties <= 0)

        self.hjd_min = np.min(self.hjd)
        self.hjd_max = np.max(self.hjd)

        # determine which gaps are usual gridpoints (as opposed to nightly gaps)
        gaps = self.hjd[1:] - self.hjd[:-1]
        ok = gaps < 1.5*np.min(gaps)
        self.hjd_step = np.round(np.median(gaps[ok])*24.0*60.0)/24.0/60.0 # rounded to nearest minute
        self.indices = np.round((self.hjd - self.hjd_min)/self.hjd_step).astype(np.int)

    def gridify(self):
        self.grid, self.regridded = {}, {}
        self.grid['hjd'] = np.arange(self.hjd_min, self.hjd_max + self.period_max, self.hjd_step)
        self.ngrid = self.grid['hjd'].shape[0]
        self.grid['depths'] = np.ma.MaskedArray(data=np.zeros((self.ndurations, self.ngrid)), mask=np.ones((self.ndurations, self.ngrid)).astype(np.bool), fill_value=0)
        self.grid['depths'][:, self.indices] = self.depths

        self.grid['uncertainties'] = np.ma.MaskedArray(data=np.zeros((self.ndurations, self.ngrid)), mask=np.ones((self.ndurations, self.ngrid)).astype(np.bool), fill_value=-1)
        self.grid['uncertainties'][:, self.indices] = self.uncertainties

        #self.grid['depths'][0,:] = self.grid['hjd']
        #self.grid['uncertainties'][0,:] = np.ones_like(self.grid['hjd'])
        self.grid['inversevariances'] = 1.0/self.grid['uncertainties']**2

    def foldall(self):
        python.origami.foldall(self)

    def plotfolding(self):
        try:
            self.ax1d
        except:
            self.fig = plt.figure(figsize=(5,5))
            self.gs = plt.matplotlib.gridspec.GridSpec(2,1,height_ratios=[1,4], hspace=0)
            self.ax1d = plt.subplot(self.gs[0])
            self.ax2d = plt.subplot(self.gs[1])
        self.plotted1d = self.ax1d.plot((self.epochs['depths']/self.epochs['uncertainties']).transpose())

        self.plotted2d = self.ax2d.imshow((self.regridded['depths']/self.regridded['uncertainties'])[0,:,:], interpolation='nearest', cmap='gray', aspect='auto')


    def plot(self, i):
        plt.errorbar(self.hjd, self.depths[i,:], self.uncertainties[i,:], alpha=0.5)
        ok = self.grid_depths[i,:].mask == False
        plt.errorbar(self.grid_hjd[ok], self.grid_depths[i,ok], self.grid_uncertainties[i,ok], alpha=0.5)
