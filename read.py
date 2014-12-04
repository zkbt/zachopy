'''Wrappers to for reading files.'''

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
	file = open(filename)

	# split it into a list of lines
	lines = file.readlines()
	lines.reverse()

	# create an empty dictionary
	levels = []
	dictionary = {}
	keytypes = {}

	# loop through the lines of the header
	while(True):
		line = lines.pop()

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
		line = lines.pop()

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
