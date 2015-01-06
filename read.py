'''Simple wrappers for reading files.'''
import astropy.io.ascii, numpy as np

def parameters(filename):
	'''Read a Z-style parameter file into a dictionary. This file should look like:

	-----------------------------

	# define some separators, making sure to leave a blank line after the header
	" = name
	' = date

	# exposures of Barnard's, to be used as the template
	"Barnard's Star"
	'140916'  1118 1119 1120
	'140917'  1119 1120 1121
	'141007'  1118 1119 1120
	'141015'  1117 1118 1119

	-----------------------------

	and will return a dictionary with which you can do something like result["Barnard's Star"]["140916"] to access a list of parameters for each row.'''

	# open a file
	file = open(filename, 'rU')

	# split it into a list of lines
	lines = file.readlines()

	# create an empty dictionary
	levels = []
	dictionary = {}
	keytypes = {}

	# loop through the lines of the header
	while(True):
		line = lines.pop(0)

		# skip comments
		if line[0] == '#':
			continue

		# stop when you get to the end of the header
		if line[0] == '\n':
			break

		chunks = line.split()
		separator = chunks[0]
		keytype = chunks[-1]
		keytypes[separator] = keytype
		levels.append(keytype)
		print " grouping lines starting with {0} under the entry '{1}'".format(separator, keytype)


	# loop through the rest of the lines
	level = dictionary
	while(len(lines)>0):
		# take the next line
		line = lines.pop(0)

		# skip comments and blanks
		if line[0] == '#':
			continue

		# reset to top level if hit a space
		if line[0] == '\n':
			continue

		separator = line[0]
		keytype = keytypes[separator]
		empty, key, data = line.split(separator)
		if keytype == levels[-1]:
			# at the innermost level, store the data
			level[key] = data.split()
		else:
			# at the outermost level, reset the to the highest level dictionary
			if keytype == levels[0]:
				level = dictionary
			# at all but the innermost level, make and move into a new level of dictionary
			level[key] = {}
			level = level[key]

	return dictionary

def table(filename, individuals=False):
	'''Use astropy, 'cause it's super convenient!

		For cool tricks with astropy tables, check out astropy.readthedocs.org'''
	return astropy.io.ascii.read(filename)

def transmissionspectrum(filename):
	'''Read a Z-style transmission spectrum file.'''

	# open a file
	file = open(filename, 'rU')
	print "Reading transmission spectrum from " + filename
	# split it into a list of lines
	lines = file.readlines()

	# first, interpret the header to learn column names and units
	noheader, nounits = True, True
	while(noheader or nounits):
		line = lines.pop(0)

		# skip comments and blanks
		if line[0] == '#' or line[0] == '\n':
			continue

		# the first uncommented line should be the headers
		if noheader:
			columns = line.split()
			noheader = False
			continue

		# the second uncommented line should be the units
		if nounits:
			units = dict(zip(columns, line.split()))
			nounits = False

	# then read the data into an astropy table
	table = astropy.io.ascii.read(lines, names=columns)

	# standardize wavelength columns' units
	wavelengthunits = dict(nm=1.0, angstrom=0.1, micron=1000.0)
	for column in ['left', 'center', 'right']:
		try:
			table[column] = table[column].astype(np.float)*wavelengthunits[units[column]]
			print ' converted ' + column + ' from ' + units[column]

		except:
			pass

	# standardize the wavelength columns into left, center, right
	if 'left' in columns and 'right' in columns:
		table.add_column(table.Column(name='center', data=(table['left'] + table['right'])/2.0),1)
	elif 'center' in columns:
		binsize = np.mean(table['center'][1:] - table['center'][:-1])
		table.add_column(table.Column(name='left', data=(table['center'] - binsize/2.0)),0)
		table.add_column(table.Column(name='right', data=(table['center'] + binsize/2.0)),2)

	# standardize depthlike columns' units
	depthlikeunits = dict(unity=1.0, ppm=1.0e-6, percent=0.01)
	for measurement in ['depth', 'rp_over_rs']:
		try:
			for column in [measurement, measurement + '_error']:
				temp = table.Column(table[column], dtype=np.float)
				table.remove_column(column)
				table.add_column(temp)
				table[column] *=depthlikeunits[units[column]]
				print ' converted ' + column + ' from ' + units[column]
		except:
			print " no " + measurement + " columns found."
	# convert depths to rp_over_rs
	if 'depth' in columns:
		rp_over_rs = table.Column(name='rp_over_rs', data=np.sqrt(table['depth']))
		rp_over_rs_error = table.Column(name='rp_over_rs_error', data=table['depth_error']/rp_over_rs/2.0)
		table.add_columns([rp_over_rs, rp_over_rs_error])
		table.remove_columns(['depth', 'depth_error'])

	print table
	return table


def mind(*args, **kwargs):
	return 42
