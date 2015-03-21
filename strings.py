import numpy as np
import parse

possiblescales = dict(degrees=360.0/24.0, radians=360.0/24.0)

def format(delimiter='letters'):
    if delimiter == 'letters':
        return "{rah:02d}h{ram:02d}m{ras:05.2f}s{sign:1}{decd:02d}d{decm:02d}m{decs:05.2f}s"
    if delimiter == ':':
        return "{rah:02d}:{ram:02d}:{ras:05.2f} {sign:1}{decd:02d}:{decm:02d}:{decs:05.2f}"

def test(n=100000, verbose=False, delimiter=':'):
    '''Test the conversion between decimals and strings, by generating lots of random positions.'''
    for i in range(n):
        ra, dec = np.random.uniform(0.0, 360.0), np.random.uniform(-90,90)
        s = clockify(ra, dec, delimiter=delimiter)
        nra, ndec = unclockify(s)
        r = clockify(nra, ndec, delimiter=':')
        if verbose:
            print
            print "performing random test #{0}".format(i)
            print ra, dec
            print s
            print nra, ndec
            print r
            print '---------------'
            print ra - nra, dec - ndec
            print
        assert(r == s)
        assert(np.abs(nra - ra) <= 0.01/3600.0*15)
        assert(np.abs(ndec - dec) <= 0.01/3600.0)
        #print r
        if i % (n/100) == 0:
            print '{0}/{1}'.format(i,n)
    print 'clocking and unclocking worked on {0} random positions'.format(n)

def unclockify(s, delimiter='letters'):
    '''Convert a positional string to decimal RA and Dec values (in degrees).'''

    if 'h' in s:
        delimiter='letters'
    if ':' in s:
        delimiter=':'

    d = parse.parse(format(delimiter).replace('{decs:05.2f}', '{decs}' ).replace('{ras:05.2f} ', '{ras} ' ), s)
    ra = 15.0*(d['rah'] + d['ram']/60.0 + np.float(d['ras'])/3600.0)
    dec = np.int(d['sign']+'1')*(d['decd'] + d['decm']/60.0 + np.float(d['decs'])/3600.0)

    return ra, dec

def clockify(ra, dec, delimiter='letters'):
    '''Convert an RA and Dec position (in degrees) to a positional string.'''


    # calculate the RA
    rah = np.floor(ra/15.0).astype(np.int)
    ram = np.floor((ra/15.0 - rah)*60.0).astype(np.int)
    ras = np.abs((ra/15.0 - rah - ram/60.0)*3600.0)



    # calculate sign
    if dec >= 0:
        sign = '+'
    else:
        sign = '-'

    # calculate the Dec
    decd = np.floor(np.abs(dec)).astype(np.int)
    decm = np.floor((np.abs(dec) - decd)*60.0).astype(np.int)
    decs = np.abs((np.abs(dec) - decd - decm/60.0)*3600.0)


    if np.round(ras, decimals=2) == 60.00:
        ras = 0.0
        ram += 1
        if ram == 60:
            ram = 0
            rah += 1
        if rah == 24:
            rah = 0

    if np.round(decs, decimals=2) == 60.00:
        decs = 0.0
        decm += 1
        if decm == 60:
            decm = 0
            decd += 1




    return format(delimiter).format(**locals())
