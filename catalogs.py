from collections import OrderedDict
from zachopy.finder import Finder
import os
import numpy as np

class Catalog:
    def __init__(self, stars=[], name='catalog'):
        '''Initialize a catalog object, from a list of stars.'''
        self.stars = stars
        for s in self.stars:
            s.entry = self.style(s)
        self.name = name

    def writeToText(self, path=''):
        '''Write catalog out to text files readable by machines and humans.'''

        self.prefix = os.path.join(path, self.name)
        with open('{}.{}'.format(self.prefix, self.suffix), 'w') as f:
            for s in self.stars:
                f.write(s.entry.machine() + '\n')

        with open('{}.forhumans'.format(self.prefix), 'w') as f:
            for s in self.stars:
                f.write(s.entry.human() + '\n')

    def createFinders(self, instrument='DIS', **kw):
        '''Use ds9 to create finder charts.'''
        for s in self.stars:
            f = Finder(star=s, instrument=instrument, **kw)


class APO(Catalog):
    '''An APO catalog object.'''
    def __init__(self, *args, **kwargs):
        self.style = APOEntry
        self.suffix = 'tui'
        Catalog.__init__(self, *args, **kwargs)


class CatalogEntry(object):
    pass

class APOEntry(CatalogEntry):
    def __init__(self, star):
        '''initialize a basic APO catalog entry, from a star object'''

        self.colnames = [   'name', # the name of the target, no spaces
                            'ra', # right ascension
                            'dec', # declination
                            'comment',
                            'RotAngle',
                            'Rot'] # the epoch of the ra and dec, for PM

        self.columns = OrderedDict()
        for col in self.colnames:
            self.columns[col] = None

        self.star = star
        self.populate()

    def populate(self, epoch=2016.9):
        self.columns['name'] = self.star.name.replace(' ', '')
        self.columns['ra'], self.columns['dec'] = self.star.posstring(epoch, delimiter=':').split()[0:2]

        for k,v in self.star.attributes.items():
            self.columns[k] = v
        try:
            self.columns['comment']
        except KeyError:
            self.columns['comment']  = ''

    def machine(self):
        f = '{name:25s} {ra:10s} {dec:9s}'
        return f.format(**self.columns)

    def human(self):
        f = '{name:25s} {ra:10s} {dec:9s} # '
        if 'V' in self.columns:
            f += 'V={V:4.1f}, '
        if 'R' in self.columns:
            f += 'R={R:4.1f}, '
        if 'I' in self.columns:
            f += 'I={R:4.1f}, '
        if 'J' in self.columns:
            f += 'J={R:4.1f}, '
        f += '{comment}'
        return f.format(**self.columns)


class Magellan(CatalogEntry):
    def __init__(self, star):
        '''initialize a basic Magellan catalog entry, from a star object'''

        self.colnames = [   'number', # a reference number
                            'name', # the name of the target, no spaces
                            'ra', # right ascension
                            'dec', # declination
                            'equinox', # equinox of coordinates
                            'pmra', # in seconds of time per year (s.ss)
                            'pmdec', # in arcseconds per year (s.ss)
                            'rotatorangle', # rotator offset angle (dd.d)
                            'rotatormode', # rotator offset mode
                            'guide1_ra', # for guide star, leave 00:00:00
                            'guide1_dec', # for guide star, leave 00:00:00
                            'guide1_equinox', # for guide star, leave 2000.0
                            'guide2_ra', # for guide star, leave 00:00:00
                            'guide2_dec', # for guide star, leave 00:00:00
                            'guide2_equinox', # for guide star, leave 2000.0
                            'epoch'] # the epoch of the ra and dec, for PM

        self.columns = OrderedDict()
        for col in self.colnames:
            self.columns[col] = None

        self.star = star
        self.populate()

    def populate(self, epoch=2016.3):
        self.columns['name'] = self.star.name.replace(' ', '')
        self.columns['ra'], self.columns['dec'] = self.star.posstring(epoch, delimiter=':').split()[0:2]
        self.columns['equinox'] = 2000.0

        magpmra = self.star.pmra/1000.0/np.cos(self.star.icrs.dec.rad)/15.0
        self.columns['pmra'] = magpmra
        magpmdec = self.star.pmdec/1000.0
        self.columns['pmdec'] = magpmdec

        for k in ['pmra', 'pmdec']:
            try:
                assert(self.self.columns[k].mask == False)
            except (AssertionError,AttributeError):
                self.columns[k] = 0.0
                print("replaced masked {0} with 0".format(k))
        # set the rotator mode to offset nothing from last position
        self.columns['rotatorangle'] = 0.0
        self.columns['rotatormode'] = 'OFF'

        # deal with non-existant guide stars
        self.columns['guide1_ra'] = '00:00:00'
        self.columns['guide1_dec'] = '+00:00:00'
        self.columns['guide1_equinox'] = '2000.0'
        self.columns['guide2_ra'] = '00:00:00'
        self.columns['guide2_dec'] = '+00:00:00'
        self.columns['guide2_equinox'] = '2000.0'

        self.columns['epoch'] = self.star.icrs.obstime.value

        for k,v in self.star.attributes.iteritems():
            self.columns[k] = v
        try:
            self.columns['comment']
        except KeyError:
            self.columns['comment']  = ''

    def machine(self):
        f = 'M{number:03.0f} {name:25s} {ra:10s} {dec:9s} {equinox:6.1f} {pmra:>5.2f} {pmdec:>5.2f} {rotatorangle:>6.1f} {rotatormode:3s} {guide1_ra} {guide1_dec} {guide1_equinox} {guide2_ra} {guide2_dec} {guide2_equinox} {epoch:6.1f}'
        return f.format(**self.columns)

    def human(self):
        f = 'M{number:03.0f} {name:25s} {ra:10s} {dec:9s} # '
        if 'V' in self.columns:
            f += 'V={V:4.1f}, '
        if 'R' in self.columns:
            f += 'R={R:4.1f}, '
        f += '{comment}'
        return f.format(**self.columns)

class MIKE(Magellan):
    def populate(self, *args, **kwargs):
        Magellan.populate(self, *args, **kwargs)
        self.columns['rotatorangle'] = 0.0
        self.columns['rotatormode'] = 'GRV'
