import numpy as np
cimport numpy as np
def foldall(self):

  for nperiod in range(200,300):
      fold(self.grid['depths'], self.grid['inversevariances'], nperiod, self.hjd_max, self.hjd_min, self.hjd_step)
      print ('{0}'.format(nperiod))

def fold(np.ndarray grid_depths, np.ndarray grid_inversevariances, np.int nperiod, np.float hjd_max, np.float hjd_min, np.float hjd_step):
    '''Take the gridified MarPLES, and fold them back every nperiod epochs.'''

    # calculate the number of cycles spanned by the data, for this nperiod
    cdef int ncycles = np.ceil((hjd_max - hjd_min)/hjd_step/nperiod)

    # figure out how big of an array to start with
    cdef int ntotal = ncycles*nperiod

    # figure out the shape of the original array, and what it's folded shape should be
    cdef int ndurations = grid_depths.shape[0]

    # regrid the depths and inversevariances, so they're folded back on one another
    regridded_depths = grid_depths[:,0:ntotal].reshape((ndurations, ncycles, nperiod))
    regridded_inversevariances = grid_inversevariances[:,0:ntotal].reshape((ndurations, ncycles, nperiod))

    # stack each period to measure the S/N at all epochs
    cdef int cycleaxis = 1
    eweights = np.sum(regridded_inversevariances, cycleaxis)


    epochs_depths = np.sum(regridded_depths*regridded_inversevariances, cycleaxis)/eweights
    epochs_uncertainties = np.sqrt(1.0/eweights)
    epochs_nboxes = np.sum(regridded_inversevariances > 0)

    epochs_chisq = np.sum((regridded_depths - epochs_depths.reshape((ndurations, 1, nperiod)))*regridded_inversevariances)
    epochs_rescaling = np.sqrt(np.maximum(epochs_chisq/(epochs_nboxes-1), 1))
    epochs_uncertainties *= epochs_rescaling
