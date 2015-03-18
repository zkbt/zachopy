zachopy
=======

Various tools used in lots of code written by Zach Berta-Thompson (zkbt@mit.edu), primarily written in Python. It's a weird combination of odds and ends, that tend to be required by lots of programs. There is absolutely no guarantee that these will work for you, but please feel free to peruse the bits of code included here. I hope something may be helpful!

They include:

Talker.py = all classes that inherit from a Talker will have access to a  ".speak('bla bla bla')" method, which does some handy labeling and indentation stuff

color.py = tools to generate colors (including nm2rgb, displaying spectrophotometric colors on computer screens)

display.py = tools to display data, mostly images or cubes of images, with ds9 or imshow or as movies

finder.py = tools to create finder charts for high-proper motion stars

iplot.py = tools to "simplify" (probably not, but at least from Zach's new-to-the-game perspective) interactive plots allowing programs to collect mouse clicks from a plot (e.g. to select a background subtraction region)

oned.py = tools for dealing with 1D arrays, including correlation functions

read.py = tools for reading particular weird file formats

regions.py = tools for dealing with ds9 region definitions

spherical.py = a few spherical coordinate transformation odds and ends

star.py = tools for getting info about a single star from SIMBAD

strings.py = tools for dealing with strings (e.g. parsing positions, etc...)

twod.py = tools for dealing with 2D arrays, including stacking and interpolation and such

units.py = a list of frequently used units

utils.py = various utilities that are kind of weird but seem to come up often
