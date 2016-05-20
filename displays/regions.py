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

	def docs(self):
		print	''' Regions

Regions provide a means for marking particular areas of an image for further analysis. Regions may also be used for presentation purposes. DS9 supports a number of region descriptions, each of which may be edited, moved, rotated, displayed, saved and loaded, via the GUI and XPA.

Region Descriptions
Region Properties
Region File Format
Composite Region
Template Region
External Region Files
Region Descriptions

Circle
Usage: circle x y radius

Ellipse
Usage: ellipse x y radius radius angle

Box
Usage: box x y width height angle

Polygon
Usage: polygon x1 y1 x2 y2 x3 y3 ...

Point
Usage: point x y # point=[circle|box|diamond|cross|x|arrow|boxcircle] [size]
       circle point x y

Line
Usage: line x1 y1 x2 y2 # line=[0|1] [0|1]

Vector
Usage: vector x1 y1 length angle # vector=[0|1]

Text
Usage: text x y # text={Your Text Here}
       text x y {Your Text Here}

Ruler
Usage: ruler x1 y1 x2 y2 # ruler=[pixels|degrees|arcmin|arcsec]

Compass
Usage: compass x1 y1 length # compass=<coordinate system> <north label> <east label> [0|1] [0|1]

Projection
Usage: projection x1 y1 x2 y2 width

Annulus
Usage: annulus x y inner outer n=#
       annulus x y r1 r2 r3...

Ellipse Annulus
Usage: ellipse x y r11 r12 r21 r22 n=# [angle]
       ellipse x y r11 r12 r21 r22 r31 r32 ... [angle]

Box Annulus
Usage: box x y w1 h1 w2 h2 [angle]
       box x y w1 h1 w2 h2 w3 h3 ... [angle]

Panda
Usage: panda x y startangle stopangle nangle inner outer nradius

Epanda
Usage: epanda x y startangle stopangle nangle inner outer nradius [angle]

Bpanda
Usage: bpanda x y startangle stopangle nangle inner outer nradius [angle]

Composite
Usage: # composite x y angle

Region Properties

Each region has a number of properties associated with the region, which indicates how the region is to be rendered or manipulated. Properties are defined for a region in the comment section of the region description. The exception is the Include/Exclude property. It is set via '+' or '-' preceding the region. In addition, the Line, Point, and Ruler regions have unique properties, not shared by others. Not all properties are available via the GUI or are applicable for all regions.

Text

All regions may have text associated with them. Use the text property to set the text. Strings may be quoted with " or ' or {}. For best results, use {}.

Example: circle(100,100,20) # text = {This message has both a " and ' in it}
Color

The color property specifies the color of the region when rendered. The follow 8 colors are supported:

Example: circle(100,100,20) # color = green
Dash List

Sets dashed line parameters. This does not render the region in dashed lines.

Example: circle(100,100,20) # dashlist = 8 3
Width

Sets the line width used to render the region.

Example: circle(100,100,20) # width = 2
Font

The font property specifies the font family, size, weight, and slant of any text to be displayed along with the region.

Example: circle(100,100,20) # font="times 12 bold italic"
Can Select

The Select property specifies if the user is allowed to select (hence, edit) the region via the GUI. For Regions used for catalogs and such, it is desirable that the user is unable to edit, move, or delete the region.
Example: circle(100,100,20) # select = 1
Can Highlite

The Highlite property specifies if the edit handles become visible when the region is selected.
Example: circle(100,100,20) # hightlite = 1
Dash

Render region using dashed lines using current dashlist value.

Example: circle(100,100,20) # dash = 1
Fixed in Size

The Fixed in Size property specifies that the region does not change in size as the image magnification factor changes. This allows the user to build complex pointer type regions.

Example: circle(100,100,20) # fixed = 1
Can Edit

The Edit property specifies if the user is allowed to edit the region via the GUI.

Example: circle(100,100,20) # edit = 1
Can Move

The Move property specifies if the user is allowed to move the region via the GUI.

Example: circle(100,100,20) # move = 1
Can Rotate

The Rotate property specifies if the user is allowed to rotate the region via the GUI.

Example: circle(100,100,20) # rotate = 1
Can Delete

The Delete property specifies if the user is allowed to delete the region via the GUI.

Example: circle(100,100,20) # delete = 1
Include/Exclude

The Include/Exclude properties flags the region with a boolean NOT for later analysis. Use '+' for include (default), '-' for exclude.

Example: -circle(100,100,20)
Source/Background

The Source/Background properties flag the region for use with other analysis applications. The default is source

Example: circle(100,100,20) # source
         circle(200,200,10) # background
Tag

All regions may have zero or more tags associated with it, which may be used for grouping and searching.

Example:  circle(100,100,20) # tag = {Group 1} tag = {Group 2}
Line

The line region may be rendered with arrows, one at each end. To indicate arrows, use the line property. A '1' indicates an arrow, '0' indicates no arrow.

Example: line(100,100,200,200) # line= 1 1
Ruler

The ruler region may display information in 'pixels', 'degrees', 'arcmin', or 'arcsec'. Use the ruler property to indicate which format to display distances in.

Example: ruler(100,100,200,200) # ruler=arcmin
Point

Point regions have an associated type and size. Use the point property to set the point type.

Example: point(100,100) # point=diamond 31
Default Properties

The default properties are:

text={}
color=green
font="helvetica 10 normal roman"
select=1
edit=1
move=1
delete=1
highlite=1
include=1
fixed=0
Region File Format

Syntax

Region arguments may be separated with either a comma or space. Optional parentheses may be used a the beginning and end of a description.

circle 100 100 10
circle(100 100 10)
circle(100,100,10)
Comments

All lines that begin with # are comments and will be ignored.

# This is a comment
Delimiter

All lines may be delimited with either a new-line or semi-colon.

circle 100 100 10
ellipse 200 200 20 40 ; box 300 300 20 40
Header

A DS9 region file may start with the following optional header:

# Region file format: DS9 version 4.0
Global Properties

Global properties affect all regions unless a local property is specified. The global keyword is first, followed by a list of keyword = value pairs. Multiple global property lines may be used within a region file.

global color=green font="helvetica 10 normal roman" edit=1 move=1 delete=1 highlite=1 include=1 wcs=wcs
Local Properties

Local properties start with a # after a region description and only affect the region it is specified with.

physical;circle(504,513,20) # color=red text={This is a Circle}
Coordinate Systems

For each region, it is important to specify the coordinate system used to interpret the region, i.e., to set the context in which the position and size values are interpreted. For this purpose, the following keywords are recognized:

PHYSICAL                # pixel coords of original file using LTM/LTV
IMAGE                   # pixel coords of current file
FK4, B1950              # sky coordinate systems
FK5, J2000              # sky coordinate systems
GALACTIC                # sky coordinate systems
ECLIPTIC                # sky coordinate systems
ICRS                    # currently same as J2000
LINEAR                  # linear wcs as defined in file
AMPLIFIER               # mosaic coords of original file using ATM/ATV
DETECTOR                # mosaic coords of original file usingDTM/DTV
Mosaic Images

While some coordinate systems are unique across mosaic images, others coordinate systems, such as image, or physical , are valid on a per segment basis. In this case, use tile to specify which header to use in all coordinate conversions. The default is the first header, or tile 1.

Example: tile 2;fk5;point(100,100)
Multiple WCS

If an image has multiple wcs's defined, use wcs# to specify which wcs to use for all wcs references. Valid values are wcs, wcsa, wcsb, wcsc... wcsz.
Example: wcsa;linear;point(100,100) # point=diamond

Specifying Positions and Sizes

The arguments to region shapes can be floats or integers describing positions and sizes. They can be specified as pure numbers or using explicit formatting directives:

position arguments

[num]                   # context-dependent (see below)
[num]d                  # degrees
[num]r                  # radians
[num]p                  # physical pixels
[num]i                  # image pixels
[num]:[num]:[num]       # hms for 'odd' position arguments
[num]:[num]:[num]       # dms for 'even' position arguments
[num]h[num]m[num]s      # explicit hms
[num]d[num]m[num]s      # explicit dms
size arguments

[num]                   # context-dependent (see below)
[num]"                  # arc sec
[num]'                  # arc min
[num]d                  # degrees
[num]r                  # radians
[num]p                  # physical pixels
[num]i                  # image pixels
When a "pure number" (i.e. one without a format directive such as 'd' for 'degrees') is specified, its interpretation depends on the context defined by the 'coordsys' keyword. In general, the rule is:

All pure numbers have implied units corresponding to the current coordinate system.

If no such system is explicitly specified, the default system is implicitly assumed to be PHYSICAL. In practice this means that for IMAGE and PHYSICAL systems, pure numbers are pixels. Otherwise, for all systems other than linear, pure numbers are degrees. For LINEAR systems, pure numbers are in the units of the linear system. This rule covers both positions and sizes. The input values to each shape can be specified in several coordinate systems including:

IMAGE                   # pixel coords of current file

LINEAR                  # linear wcs as defined in file
FK4, B1950              # sky coordinate systems
FK5, J2000
GALACTIC
ECLIPTIC
ICRS
PHYSICAL                # pixel coords of original file using LTM/LTV
AMPLIFIER               # mosaic coords of original file using ATM/ATV
DETECTOR                # mosaic coords of original file using DTM/DTV

WCS,WCSA-WCSZ           # specify which WCS system to be used for
                        # linear and sky coordinate systems

If no coordinate system is specified, PHYSICAL is assumed. PHYSICAL or a World Coordinate System such as J2000 is preferred and most general. The coordinate system specifier should appear at the beginning of the region description, on a separate line (in a file), or followed by a new-line or semicolon; e.g.,

image; circle 100 100 10
physical; ellipse 200 200 10 20
fk5; point 30 50
wcsa; fk4; point 202 47
wcsp; linear; point 100 100
The use of celestial input units automatically implies WORLD coordinates of the reference image. Thus, if the world coordinate system of the reference image is J2000, then

circle 10:10:0 20:22:0 3'
is equivalent to:
j2000; circle 10:10:0 20:22:0 3'
Note that by using units as described above, you may mix coordinate systems within a region specifier; e.g.,

physical; circle 6500 9320 3'
Note that, for regions which accept a rotation angle such as:

ellipse (x, y, r1, r2, angle)
box(x, y, w, h, angle)
the angle is relative to the specified coordinate system. In particular, if the region is specified in WCS coordinates, the angle is related to the WCS system, not x/y image coordinate axis. For WCS systems with no rotation, this obviously is not an issue. However, some images do define an implicit rotation (e.g., by using a non-zero CROTA value in the WCS parameters) and for these images, the angle will be relative to the WCS axes. In such case, a region specification such as:

fk4;ellipse(22:59:43.985, +58:45:26.92,320", 160", 30)
will not, in general, be the same region specified as:

physical;ellipse(465, 578, 40, 20, 30)
even when positions and sizes match. The angle is relative to WCS axes in the first case, and relative to physical x,y axes in the second.

Composite Region

A Composite Region is a region which is a collection of other regions, which share common properties. A composite region is composed of a center point and a rotation angle, of which all its members are rendered in reference to. A composite region is defined by the # composite x y angle declaration followed by a number of regions who are or'd together. A composite region is manipulated as a single region within ds9. A composite region maybe created from the current selection of regions by selecting the Create Composite Region menu option. Likewise, a composite region can be dissolved by selecting the Dissolve Composite Region menu option.

Template Region

A Template Region is a special form of a region which is saved in a special wcs coordinate system WCS0. WCS0 indicates that the ra and dec values are relative to the current WCS location, not absolute. A template region can be loaded at any location into any fits image which contains a valid wcs. For example, a user may create a series of regions, which represent an instrument template. Then, by selecting the Save As Template menu option, a template region saved. The user may now load this templated into any other fits image which contains a valid WCS.

External Region Files

DS9 can read and write a number of region file formats. Not all formats support all the functionality of DS9 regions. Therefore, the user may loose some information when writing and then reading back from a region file in a format other that DS9. On output, the regions File Format menu or the XPA regions point is used specify the output coordinate system and format. On input, the menu or xpa point is used only for the X Y format. For all other formats, the input coordinate system is specified in the regions file itself.

Funtools
TEXT is ignored
VECTOR is ignored
PROJECTION is ignored
RULER is ignored
COMPASS is ignored
FIELD is ignored
PIE is ignored
All properties are ignored
CIAO
All point regions are translated as POINT
BOX is translated as ROTBOX
LINE is ignored
VECTOR is ignored
RULER is ignored
COMPASS is ignored
TEXT is ignored
PROJECTION is ignored
ELLIPSE ANNULUS is ignored
BOX ANNULUS is ignored
PANDA is translated as PIE
EPANDA is ignored
BPANDA is ignored
All properties are ignored
SAOimage
All point regions are translated as POINT
LINE is ignored
VECTOR is ignored
TEXT is ignored
PROJECTION ignored
PROJECTION3D is ignored
RULER is ignored
COMPASS is ignored
PANDA is ignored
EPANDA is ignored
BPANDA is ignored
All properties are ignored
IRAF PROS
All point regions are translated as POINT
LINE is ignored
VECTOR is ignored
TEXT is ignored
RULER is ignored
COMPASS is ignored
PROJECTION ignored
PROJECTION3D is ignored
PANDA is ignored
EPANDA is ignored
BPANDA is ignored
All properties are ignored
FITS REGION Binary Table
Read Only. DS9 currently can not write in this format.
POINT is translated into BOX CIRCLE POINT
ROTBOX is translated into BOX
RECTANGLE is translated into BOX
ROTRECTANGLE is translated into a BOX
PIE is translated into PANDA
The follow regions are not supported
ELLIPTANNULUS
SECTOR
DIAMOND
RHOMBUS
ROTDIAMOND
ROTRHOMBUS
X Y
This format consists of a number of coordinate pairs, one per line. The coordinate format for both input and output is specified via the Save Regions Parameters menu or XPA regions point. The first two coordinates are read, the rest of the line is ignored. The comment character '#' may be used at the beginning of line and the line is ignored. This format is very useful for reading in coordinates from other external analysis programs, such as IRAF.

Example: # this is a comment
physical # this overrides the specified coordinate system
300 300
400 400 # this is a comment '''
