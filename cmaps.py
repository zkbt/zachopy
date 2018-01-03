import matplotlib.colors as co
import numpy as np

def name2color(name):
	"""Return the 3-element RGB array of a given color name."""
	return co.hex2color(co.cnames[name])

def one2another(bottom='white', top='red', alphatop=1.0, alphabottom=1.0, N=256):
	'''
	Create a cmap that goes smoothly (linearly in RGBA) from "bottom" to "top".
	'''
	rgb_bottom, rgb_top = name2color(bottom), name2color(top)
	r = np.linspace(rgb_bottom[0],rgb_top[0],N)
	g = np.linspace(rgb_bottom[1],rgb_top[1],N)
	b = np.linspace(rgb_bottom[2],rgb_top[2],N)
	a = np.linspace(alphabottom, alphatop,N)
	colors = np.transpose(np.vstack([r,g,b,a]))
	cmap = co.ListedColormap(colors, name='{bottom}2{top}'.format(**locals()))
	return cmap

if __name__ == '__main__':
	import matplotlib.pyplot as plt
	print("This is a test of colormaps with one2another().")
	fascinating = one2another('seagreen', 'indigo')
	x = np.arange(100)
	y = x + np.random.normal(0, 1, 100)
	plt.scatter(x, y, s=100, c=x, cmap=fascinating, vmin=0, vmax=100)
	plt.colorbar()
	plt.show()
