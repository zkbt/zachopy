# -*- coding: iso-8859-1 -*-
import astropy.table, astropy.time, astropy.io.ascii
import numpy as np
import os, sys, glob
import star_to_files
import scipy.io

from zachopy.Talker import Talker
maximum_delay = 5 # days

mittens_data = os.getenv('MITTENS_DATA')
class hemisphere(Talker):
  def __init__(self, remake=False):
    Talker.__init__(self, line=80)
    self.db = star_to_files.db
    self.load(remake=remake)
  
  @property
  def n(self):
    return len(self.table)
    
  @property
  def filename(self):
    return mittens_data + 'population/'+self.__class__.__name__ + '_progress.dat'
    
  def save(self):
    astropy.io.ascii.write(self.table, self.filename)
    self.speak('saved to {0}'.format(self.filename))
    
  def load(self, remake=False):
    try:
      assert(remake == False)
      t = astropy.time.Time(os.stat(self.filename).st_mtime, format='unix')
      assert((t.now() - t).jd < maximum_delay)
      self.table = astropy.table.Table(astropy.io.ascii.read(self.filename))
      self.speak('loaded table from {0}'.format(self.filename))
    except:
      self.table = astropy.table.Table(masked=True)
      self.loadmo()
      self.populatemodifiedtimes()
      self.save()
  
    
  @property
  def lags(self):
    self.speak('calculating how out-of-date each component of each star is')
    temp = self.table.copy()
    now = astropy.time.Time.now().unix
    for c in temp.columns:
      if c == 'mo' or c[0] == 'n':
	continue
      #ok = np.array((temp[c] != None)).nonzero()[0]
      ok = np.arange(len(temp[c]))
      t = astropy.time.Time(temp[c][ok], format='unix')
      lag = (t.now() - t)
      temp[c] = (self.table[c] - now)/24.0/60.0/60.0
      temp[c].format='{0:0.2f}'
    return temp

  def populatefilenames(self):
    self.speak("looping through all northern stars, populating their directories with filename lists")
    for mo in self.table['mo']:
      self.speak(mo)
      star_to_files.one_star(mo)

  def populatemodifiedtimes(self):
    self.check('info', 'mo_info.idl')
    self.check('filenames', 'files.txt')
    self.check('lightcurves', 'lastloadedfiles.txt')
    self.check('marples', 'combined/box_pdf.idl')
    self.check('periodic', 'combined/phased_candidates.idl')
 
 
  
  def check(self,  label, filename ):
    self.speak('checking {0} to see when {1} files were last modified'.format(label, filename))
    
    self.table[label] = astropy.table.MaskedColumn(np.zeros(self.n),mask=np.zeros(self.n).astype(np.bool))
    count = label == 'filenames' or label == 'lightcurves'
    if count:
      self.table['n' + label] =  astropy.table.MaskedColumn(np.zeros(self.n).astype(np.int), mask=np.zeros(self.n).astype(np.bool))
    for i in range(len(self.table)):
      f = mittens_data + 'mo{0}/{1}'.format(self.table['mo'][i], filename)
      try:
	self.table[label][i] = (astropy.time.Time(os.stat(f).st_mtime, format='unix')).unix
	#self.speak('{0} {1}'.format(self.table[i]['mo'], self.table[label][i]))s
	if count:
	  self.table['n'+label][i] = len(open(f).readlines())
      except OSError:
	self.table[label].mask[i] == True

	
class north(hemisphere):
  def __init__(self, **kwargs):
    hemisphere.__init__(self, **kwargs)
  
  def loadmo(self):
    self.speak('loading MEarth objects from the Northern database')
    cmd = 'select twomass from observed'
    cur = self.db.cursor()      ## set up
    cur.execute(cmd)        	## execute command
    rows = cur.fetchall()   	## get answer
    self.table['mo'] = [r[0] for r in rows]

class both(hemisphere):
  def __init__(self, **kwargs):
    hemisphere.__init__(self, **kwargs)
  
  def loadmo(self):
    self.speak('loading MEarth objects from the merged Northern and Southern tables (population/mo_ensemble.idl')
    self.properties = astropy.table.Table(scipy.io.readsav(mittens_data + 'population/mo_ensemble.idl')['mo_ensemble'])
    self.table['mo'] = self.properties['MO']

def filenames2mo(filenames):
  return [f.split('/mo')[-1].split('/')[0] for f in filenames]