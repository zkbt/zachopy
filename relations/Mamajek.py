from Relation import *

class Mamajek(Relation):
    '''Eric Mamajek's relations for stars, linking spectral type, effective temperature, bolometric corrections, colors, abosolute magnitudes, luminosities, and mass,'''
    def __init__(self, filename='data/mamajek_dwarfproperties.dat'):
        Relation.__init__(self, filename)
