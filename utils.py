'''Utilities often used by Zach B-T.'''
import os
import numpy as np
import matplotlib.pyplot as plt

# a mkdir that doesn't complain
def mkdir(path):
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
    idx = (np.abs(array-value)).argmin()
    if verbose:
    	print "{0} --> {1}".format(value, array[idx])
    return array[idx]


# modified from above
def find_two_nearest(array,value,verbose=False):
	# assumes ordered arrays and that value falls between the min and max of the array
	offset = array-value
	idx = (np.abs(offset)).argmin()

	if np.sign(offset[idx]) == -1*np.sign(offset[idx-1]):
		nearest =  [array[idx-1], array[idx]]
	else:
	   	nearest =  [array[idx], array[idx+1]]
	if verbose:
		print "{0} is between {1} and {2}".format(value, nearest[0], nearest[1])
	return nearest

def truncate(str, n=12, etc=' ...'):
	if len(str) > n:
		return str[0:n-len(etc)] + etc
	else:
		return ("{0: ^%d}" % n).format(str)

def mad(x):
	med = np.median(x)
	return np.median(np.abs(x - med))
