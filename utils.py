'''Utilities often used by Zach B-T. These are mostly weird, small things.'''
import os

import numpy as np


def mkdir(path):
	'''A mkdir that doesn't complain if it fails.'''
	try:
		os.mkdir(path)
	except:
		pass

# stolen from the internet (SciPy cookbook)
def rebin(a, *args):
    '''rebin ndarray data into a smaller ndarray of the same rank whose dimensions
    are factors of the original dimensions. eg. An array with 6 columns and 4 rows
    can be reduced to have 6,3,2 or 1 columns and 4,2 or 1 rows.
    example usages:
    >>> a=rand(6,4); b=rebin(a,3,2)
    >>> a=rand(6); b=rebin(a,2)
    '''
    shape = a.shape
    lenShape = len(shape)
    factor = np.asarray(shape)/np.asarray(args)
    evList = ['a.reshape('] + \
             ['args[%d],factor[%d],'%(i,i) for i in range(lenShape)] + \
             [')'] + ['.sum(%d)'%(i+1) for i in range(lenShape)] + \
             ['/factor[%d]'%i for i in range(lenShape)]
    #print ''.join(evList)
    return eval(''.join(evList))

# stolen from the internet (SciPy cookbook)
def rebin_total(a, *args):
    '''rebin ndarray data into a smaller ndarray of the same rank whose dimensions
    are factors of the original dimensions. eg. An array with 6 columns and 4 rows
    can be reduced to have 6,3,2 or 1 columns and 4,2 or 1 rows.
    example usages:
    >>> a=rand(6,4); b=rebin(a,3,2)
    >>> a=rand(6); b=rebin(a,2)
    '''
    shape = a.shape
    lenShape = len(shape)
    factor = np.asarray(shape)/np.asarray(args)
    evList = ['a.reshape('] + \
             ['args[%d],factor[%d],'%(i,i) for i in range(lenShape)] + \
             [')'] + ['.sum(%d)'%(i+1) for i in range(lenShape)]
    #print ''.join(evList)
    return eval(''.join(evList))

#swiped from stack overflow
def find_nearest(array,value,verbose=False):
    idx = (np.abs(np.array(array)-value)).argmin()
    if verbose:
        print("{0} --> {1}".format(value, array[idx]))
    return array[idx]

# modified from above
def find_two_nearest(array,value,verbose=False):
	# assumes ordered arrays and that value falls between the min and max of the array
	offset = value - np.array(array)
	signs = np.sign(offset)

	# handle 1-element arrays
	if len(array) == 1:
		return [array[0], array[0]]


	if (signs == -1).all() | (signs == 1).all():
		# value is below the minimum of the array
		m = np.argmin(np.abs(offset))
		left, right = m, m
	else:
		# the value is somewhere in the bounds between the array's min and max
		left = (signs[1:] - signs[0:-1]).nonzero()[0][0]
		right = left + 1

	nearest = [array[left], array[right]]

	if verbose:
		print
		for k in locals().keys():
			print('{0:>10} = {1}'.format(k, locals()[k]))
		print
	return nearest

def interpolation_weights(bounds, value, verbose=True):

	if bounds[0] == bounds[1]:
		return 1.0, 0.0
	assert((value >= np.min(bounds)) * (value <= np.max(bounds)))
	span = np.float(bounds[1] - bounds[0])
	weights = [(bounds[1] - value)/span, (value - bounds[0])/span]
	return weights



def truncate(str, n=12, etc=' ...'):
	'''If a string is too long, truncate it with an "etc..."'''
	if len(str) > n:
		return str[0:n-len(etc)] + etc
	else:
		return ("{0: ^%d}" % n).format(str)

def mad(x):
	'''Median absolute deviation from the median.'''
	med = np.median(x)
	return np.median(np.abs(x - med))
