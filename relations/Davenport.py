from Relation import *

class Davenport(Relation):
    '''Jim Davenport's stellar color locus from SDSS, 2MASS, and Sloan.'''
    def __init__(self, filename='data/davenport_stellarlocus.dat'):
        Relation.__init__(self, filename)
