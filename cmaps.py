import matplotlib.colors as co
import numpy as np, scipy.interpolate

def name2color(name):
    """Return the 3-element RGB array of a given color name."""
    return co.hex2color(co.cnames[name])

def one2another(bottom='white', top='red', alphatop=1.0, alphabottom=1.0, N=256):
    rgb_bottom, rgb_top = name2color(bottom), name2color(top)
    r = np.linspace(rgb_bottom[0],rgb_top[0],N)
    g = np.linspace(rgb_bottom[1],rgb_top[1],N)
    b = np.linspace(rgb_bottom[2],rgb_top[2],N)
    a = np.linspace(alphabottom, alphatop,N)
    colors = np.transpose(np.vstack([r,g,b,a]))
    cmap = co.ListedColormap(colors, name='{bottom}2{top}'.format(**locals()))
    return cmap

#anchors = ['red', 'orange','yellow','green','blue','purple', 'red']
#cycle = []
#for i in range(len(anchors)-1):
#    cycle.append(new(anchors[i], anchors[i+1]))
