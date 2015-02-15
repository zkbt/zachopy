from Relation import *

class Mamajek(Relation):
    '''Relations for stars, linking spectral type, effective temperature, bolometric corrections, colors, abosolute magnitudes, luminosities, and mass,'''
    def __init__(self, filename='data/mamajek.dat'):
        Relation.__init__(self, filename)
