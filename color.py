'''Various tools for getting (sometimes astrophysically relevant) colors for plotting.'''
import colormath.color_objects
import colormath.color_conversions
import matplotlib.pyplot as plt
import numpy as np

import matplotlib.colors as co

def name2color(name):
    """Return the 3-element RGB array of a given color name."""
    return co.hex2color(co.cnames[name].lower())


def nm2rgb(inputnm, intensity=1.0):
	'''Convert a wavelength (or uniform range of wavelengths) into RGB colors usable by Python.'''
	if np.min(inputnm) <= 350.0 or np.max(inputnm) >= 800.0:
		return 0,0,0

	# create an SED, with 10 nm increments
	wavelengths = np.arange(340.0, 840.0, 10.0)
	intensities = np.zeros_like(wavelengths)

	# add monochromatic light, if the input wavelength has only one value
	nm = np.round(np.array(inputnm)/10.0)*10.0
	which = (wavelengths >= np.min(nm)) & (wavelengths <= np.max(nm))

	# wtf are the units of intensity to feed into SpectralColor?
	intensities[which]= 5.0/np.sum(which)*intensity
	spectral = colormath.color_objects.SpectralColor(*intensities)
	rgb = colormath.color_conversions.convert_color(spectral, colormath.color_objects.sRGBColor)
	return rgb.clamped_rgb_r, rgb.clamped_rgb_g, rgb.clamped_rgb_b

def monochromaticdemo():
	'''Test of nm2rgb, for a single wavelength.'''
	n = 1000
	x = np.linspace(340, 1000, n)
	colors = [nm2rgb(c) for c in x]
	plt.ion()

	plt.cla()
	fi, ax = plt.subplots(2,1, sharex=True)
	ax[0].plot(x, [c[0] for c in colors], color='red')
	ax[0].plot(x, [c[1] for c in colors], color='green')
	ax[0].plot(x, [c[2] for c in colors], color='blue')
	ax[1].scatter(x, np.random.normal(0,1,n), color= colors, s=100)
	ax[1].set_xlim(min(x), max(x))

def broadbanddemo(width=50):
	'''Test of nm2rgb, for a range of wavelengths.'''

	n = 1000
	x = np.linspace(340, 1000, n)
	colors = [nm2rgb([c-width, c+width]) for c in x]
	plt.ion()

	plt.cla()
	fi, ax = plt.subplots(2,1, sharex=True)
	ax[0].plot(x, [c[0] for c in colors], color='red')
	ax[0].plot(x, [c[1] for c in colors], color='green')
	ax[0].plot(x, [c[2] for c in colors], color='blue')
	ax[1].scatter(x, np.random.normal(0,1,n), color= colors, s=100)
	ax[1].set_xlim(min(x), max(x))
