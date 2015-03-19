from Relation import *

class Covey(Relation):
    '''Kevin Covey's synthetic SDSS/2MASS photometry of the solar metallicity Pickles stellar standards (limited to dwarfs).'''
    def __init__(self, filename='data/covey_photometryofpickles.dat'):
        Relation.__init__(self, filename)
        self.table = self.table[self.table['LClass'] == 'V']
