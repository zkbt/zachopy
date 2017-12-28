'''Wrapper to generate ds9 region files, for sketching on FITS images in ds9.'''
import string

class Regions():
	def __init__(self, name, units='physical', path=''):
		self.name = name
		self.filename = path + self.name + '.reg'
		self.regions = []
		self.addHeader()
		self.addUnits(units)

	def addUnits(self, units='physical'):
		self.units = units

	def addHeader(self):
		self.header = '# Region file format: DS9 version 4.1\n'
		self.header += '# Filename: {0}\n'.format(self.filename)
		self.header += 'global color=magenta width=2 font="helvetica 10 bold roman" select=1 highlite=1 dash=0 fixed=0 edit=1 move=1 delete=0'

	def options(self, options):
		line = ''
		if len(options.keys()) > 0:
			line += ' # '
		for key, value in options.items():
			if key == 'text' or key == 'font':
				line += key + '=' + '{' + str(value) + '}' + ' '
			else:
				line += key + '=' + str(value)  + ' '

		return line

	def addCircle(self, x, y, size=10, **kwargs):
		line = self.units + "; "
		line += "circle({0},{1},{2})".format(x, y, size) + self.options(kwargs)
		self.regions.append(line)

	def addText(self, x, y, text='bla!', size=10, **kwargs):
		line = self.units + "; "
		line += "text({0},{1},{2})".format(x, y, '{' + text +'}') + self.options(kwargs)
		self.regions.append(line)


	def addCompass(self, x, y, size=10, **kwargs):
		line = "# compass({0},{1},{2}) compass=fk5 'N' 'E' 1 1".format(x, y, size) + self.options(kwargs)
		self.regions.append(line)

	def addBox(self, x, y, w, h, **kwargs):
		line = self.units + "; "
		line += "box({0},{1},{2},{3})".format(x,y,w,h) + self.options(kwargs)
		self.regions.append(line)

	def addLine(self, x1, y1, x2, y2, **kwargs):
		line = self.units + "; "
		line += "line({0},{1},{2},{3})".format( x1, y1, x2, y2) + self.options(kwargs)
		self.regions.append(line)

	def write(self, filename=None):
		if filename is None:
			filename = self.filename
		f = open(filename, 'w')
		f.writelines(str(self))
		f.close

	def __str__(self):
		lines = [self.header, self.units]
		lines.extend(self.regions)
		return string.join(lines, '\n')
