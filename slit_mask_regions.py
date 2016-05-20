# create a regions file for ds9 that includes only the comparison stars that made it onto the slit mask
# requires slit mask input file (like, from Magellan)
# Author: Hannah Diamond-Lowe
# Date: 26 Fab 2016

from astropy.io import ascii


def slit_mask_regions(input_file, output_file_name='output.reg', circle_color='blue'):
    '''
    Takes: input_file         (str)  name and type of file, e.g. 'inputs.txt'
           output_file_name   (str)  name of your output file e.g. 'my_output_file' (no file type)
           circle_color       (str)  what color do you want your circles to be in ds9? common options are blue, red, and green
    '''

    mask_input = ascii.read(input_file)
    # inputs file columns: star_name    RA[hms]     Dec[dms]    magnitude   width[arcsec]   shape(2=rectangle)  length(->) length(<-)   position_angle_relative_to_slit

    name = 'col1'
    RA = 'col2'
    Dec = 'col3'

    f = open(output_file_name + '.reg', 'w')
    f.write('# Region file format: DS9 version 4.0 \n')
    f.write('global color=' + circle_color + ' font="helvetica 10 normal roman" edit=1 move=1 delete=1 highlite=1 include=1 wcs=wcs \n\n')

    for s in range(len(mask_input[name])):
        if 'sky' in mask_input[s][name]:
            continue
        f.write('fk5;circle(' + mask_input[s][RA] + ',' + mask_input[s][Dec] + ', 15") \n')

    f.close()
