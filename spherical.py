'''Some spherical coordinate tools.'''
import numpy as np
import astropy.coordinates

# use matrices to handle the rotations due to jitter
def rx(theta):
  return np.mat([[1, 0, 0], [0, np.cos(theta), -np.sin(theta)], [0, np.sin(theta), np.cos(theta)]])
def ry(theta):
  return np.mat([[np.cos(theta), 0, np.sin(theta)],[0, 1, 0], [-np.sin(theta), 0, np.cos(theta)]])
def rz(theta):
  return np.mat([[np.cos(theta), -np.sin(theta), 0],[np.sin(theta), np.cos(theta), 0], [0, 0, 1]])
def rotate(ra, dec, x, y):
  cart = np.transpose(np.mat(astropy.coordinates.spherical_to_cartesian(1,dec*np.pi/180, ra*np.pi/180)))
  #assert(x==0.0)
  rotated = rx(x*np.pi/180)*ry(y*np.pi/180)*cart
  #print cart
  #print ' --> '
  #print rotated
  sphe = np.array(astropy.coordinates.cartesian_to_spherical(rotated[0,0], rotated[1,0], rotated[2,0]))*180/np.pi
  print "      {0:f}, {1:f} --> {2:f},{3:f}".format(ra, dec, sphe[2], sphe[1])
  return sphe[2], sphe[1]
