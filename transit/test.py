import Planet, Star, Instrument, TM, TLC
import numpy as np 	
if True:#__name__ == '__main__':
	p = Planet.Planet()
	s = Star.Star()
	i = Instrument.Instrument()
	tm = TM.TM(planet=p, star=s, instrument=i)
	
	bjd = np.linspace(p.t0.value - p.duration*1, p.t0.value + p.duration*1, 300)
	fluxerr = 0.001*np.ones_like(bjd)
	tlc = TLC.TLC(bjd, np.ones_like(bjd), fluxerr)
	tlc.linkModel(tm)
	m = tm.planet_model(t=bjd)
	tlc.flux = m+np.random.normal(0, 1, len(bjd))*fluxerr
	tm.planet.rp_over_rs.float(0.1, [0.05, 0.15])
	tm.instrument.C.float(1, [0.99,1.01])
	tm.fastfit()
	a = raw_input('How did you feel about this test?')
	#tlc.plot()
	#tm.plot()
	
'''	def demo(self):
		parm = self.ebparams
		
		# Simple (but not astronomer friendly) dump of model parameters.
		print "Model parameters:"

		for name, value, unit in zip(eb.parnames, parm, eb.parunits):
		  print "{0:<10} {1:14.6f} {2}".format(name, value, unit)

		# Derived parameters.
		vder = eb.getvder(parm)#, -61.070553, ktot)

		print "Derived parameters:"

		for name, value, unit in zip(eb.dernames, vder, eb.derunits):
		  print "{0:<10} {1:14.6f} {2}".format(name, value, unit)

		# Phases of contact points.
		(ps, pe, ss, se) = eb.phicont(parm)
		if ps > 0.5:
		  ps -= 1.0

		# Use max(duration) for sampling range.
		pdur=pe-ps
		sdur=se-ss
		if pdur > sdur:
		  mdur = pdur
		else:
		  mdur = sdur

		# ...centered on the average of start and end points.
		pa=0.5*(ps+pe)
		sa=0.5*(ss+se)

		# Generate phase array: primary, secondary, and out of eclipse
		# in leading dimension.
		phi = np.empty([3, 1000], dtype=np.double)
		phi[0] = np.linspace(pa-mdur, pa+mdur, phi.shape[1])
		phi[1] = np.linspace(sa-mdur, sa+mdur, phi.shape[1])
		phi[2] = np.linspace(-0.25, 1.25, phi.shape[1])

		# All magnitudes.
		typ = np.empty_like(phi, dtype=np.uint8)
		typ.fill(eb.OBS_MAG)

		# These calls both do the same thing.  First, phase.
		#y = eb.model(parm, phi, typ, eb.FLAG_PHI)
		# Alternative using time.
		t = parm[eb.PAR_T0] + phi*parm[eb.PAR_P]
		y = eb.model(parm, t, typ)
		# Plot eclipses in top 2 panels.  Manual y range, forced same on
		# both plots.  x range is already guaranteed to be the same above.
		ymin = y.min()
		ymax = y.max()
		yrange = ymax - ymin

		plt.subplot(2, 2, 1)
		plt.ylim(ymax+0.05*yrange, ymin-0.05*yrange)
		plt.plot(phi[0], y[0])

		plt.plot([ps, ps], [ymax, ymin], linestyle='--')
		plt.plot([pe, pe], [ymax, ymin], linestyle='--')

		plt.subplot(2, 2, 2)
		plt.ylim(ymax+0.05*yrange, ymin-0.05*yrange)
		plt.plot(phi[1], y[1])

		plt.plot([ss, ss], [ymax, ymin], linestyle='--')
		plt.plot([se, se], [ymax, ymin], linestyle='--')

		# Out of eclipse plot across the bottom with 5*sigma clipping, robust
		# MAD estimator.
		median = np.median(y[2])
		adiff = np.absolute(y[2]-median)
		sigma = 1.48*np.median(adiff)
		tmp = np.compress(adiff < 5*sigma, y[2])

		if len(tmp) > 0:
			ymin = tmp.min()
			ymax = tmp.max()
			yrange = ymax - ymin
		else:
			ymin, ymax, yrange = 0.0, 0.0, 0.001
		plt.subplot(2, 1, 2)
		plt.ylim(ymax+0.05*yrange, ymin-0.05*yrange)
		plt.plot(phi[2], y[2])

		plt.show()
'''