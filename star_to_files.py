# -*- coding: iso-8859-1 -*-
"""
Created on Thu Jan 29 12:03:26 2015

Find the list of files associated with a MEarth LSPM or twomass ID.
Inputs should be "1234" (or lspm1234) or "12345678+12345678" (for 2mass[etc])

@author: enewton
"""

import pgdb    
import os

global mittens_data
mittens_data='/data/mearth2/marples/'

db = pgdb.connect()

#####
## get the field name and 2mass id for a given LSPM star
def read_by_db(lspm, get_lspm=False):
    
    try: ## northern are intergers
        star = int(lspm)
    except: ## if not integer, had better be string
        star = lspm

    #db = pgdb.connect() ## connect to database

    # try query
    try:
        if get_lspm:            ## use twomass to get lspm
            cmd = "select observed.field, nc.twomass \
                    from observed join nc on observed.lspmn = nc.lspmn \
                    where nc.twomass='%s';" % star
        else:                   ## use lspm to get twomass
            cmd = "select observed.field, nc.twomass \
                    from observed join nc on observed.lspmn = nc.lspmn \
                    where nc.lspmn='%s';" % star
                    
        cur = db.cursor()       ## set up
        cur.execute(cmd)        ## execute command
        rows = cur.fetchall()   ## get answer
        assert len(rows) == 1   ## should only be one match
        field = rows[0][0]
        twomass = rows[0][1]
        return field, twomass   ## return, if it worked
           
    # give up if that didn't work
    except:
        db.rollback()       ## have to stop db execution
        return False, False


#####
# read normal MEarth daily files
# daily files only contain the current filter set up
def get_files(star, 
                  allyears=False, ## use most recent seasons only
                  remove_off=False, ## don't remove the offset keyword
                  fit_meridian=False, ## fit for regular DC offsets, not jsut meridian flip
                  verbose=1):
    
    # data locations
    south = '/data/mearth2/south/reduced/tel'
    north = '/data/mearth1/reduced/tel'
    north_2008 = '/data/mearth2/2008-2010-iz/reduced/tel'
    north_2010 = '/data/mearth2/2010-2011-I/reduced/tel'

    # list of telescopes
    tels = [1,2,3,4,5,6,7,8,11,12,13,14,15,16,17,18]

    # assume star is an lspm number; get field and twomass
    field, twomass = read_by_db(star)
    if field:               ## if success
        lspm = star         ## ... an lspm number was supplied
        if verbose > 0:
            print "MITTENS:star_to_files: LSPM number was supplied, star is northern."
    # assume star is a twomass number; get field and lspm number
    else:
        field, lspm = read_by_db(star, get_lspm=True)
        if field:           ## if success 
            twomass = star  ## ... a 2mass id was supplied
            if verbose > 0:
                print "MITTENS:star_to_files: 2MASS number was supplied, star is northern."
        else:               ## if still failure
            twomass = star  ## ... just hope a southern 2mass id was supplied
            if verbose > 0:
                print "MITTENS:star_to_files: database match failed, hopefully you supplied a southern 2MASS number."

    if verbose > 0:
        print "........  lspm = ", lspm
        print "........ field = ", field
        print "........ 2mass = ", twomass

 
    files = []    
    # loop through the telescopes, see if file is there
    for tel in tels:

        # file names are different for north, south
        if tel > 10: # southern telescopes
            dirs = [south]
            suffix = ['daily']
        else: # northern telescopes
            dirs = [north_2008, north_2010, north]
            suffix = ['lc','lc','daily']
   
        for i in range(0,len(dirs)):
            base = dirs[i]
            suff = suffix[i]
            if field: ## northern target by field name
                file = base.rstrip() + str(tel).zfill(2) + '/master/' + field + '_'+suff+'.fits'
            elif lspm: ## lspm number 
                file = base.rstrip() + str(tel).zfill(2) + '/master/' + 'lspm' + '_'+suff+'.fits'
            else: ## 2massj
                file = base.rstrip() + str(tel).zfill(2) + '/master/' + '2massj' + str(star) + '_'+suff+'.fits'
            if verbose > 0:
                print "MITTENS:star_to_files: trying to find file ", file
            if os.path.isfile(file):
                files.append(file)
                if verbose > 0: 
                    print "... Found file."
   
    return twomass, files       

# run query and make files for one star
def one_star(star, verbose=0):
    
    twomass, files = get_files(star, verbose=verbose)
    stardir = mittens_data+'mo'+twomass
    starfile = 'files.txt'
    if os.path.isdir(stardir) is False:
        os.makedirs(stardir)
    fo = open(stardir+'/'+starfile, "wb")
    for f in files:
        fo.write(f +'\n')
        print '             ' + f
    fo.close()
    print "          have been written to dir", stardir
            
# run for all northern stars 
def all_north():
    print "looping through all northern stars, populating their directories with filename lists"
  
    if True:
    #db = pgdb.connect() ## connect to database
        cmd = 'select twomass from observed'
        cur = db.cursor()       ## set up
        cur.execute(cmd)        ## execute command
        rows = cur.fetchall()   ## get answer
        
        for i in rows:
            print
            print i
            one_star(i[0])
    if False:#	except:
        db.rollback()       ## have to stop db execution
       