#!/usr/bin/env python

"""This script produces a measure of the irregularity of
a waveform.  It is zero if the waveform is precisely periodic.
It is approximately 1 for white noise.

This is used as the aperiodicity measure in
Kochanski, Coleman, Grabe and Rosner JASA 2005.
"""

import math
import Num
import gpkimgclass
import power
import die
import voice_misc

DT = 0.010	# Output sampling interval.
DELTA_DELAY = 1.0/(1200.0 * 2 * math.pi)
# DELTA_DELAY is chosen so that we can align the oscillations
# at the first formant (f1 is normally under 1200 Hz)
# to an accuracy of 1 radian or less.

Fmin = 50.0
Fmax = 500.0
Fhp = 500.0
WINDOW = 0.020

DBG = None

def one_predict(d, delay, dt, Dt):
	zl = Num.zeros((delay/2,), Num.Float)
	zr = Num.zeros((delay-delay/2,), Num.Float)
	dtmp = Num.concatenate( (zl, d, zr) )
	tmp = dtmp[delay:] - dtmp[:-delay]
	assert tmp.shape == d.shape
	return power.smooth(tmp*tmp, dt, Dt, extra=WINDOW)

def predict_err(d, delays, dt, Dt):
	o = None
	for delay in delays:
		tmp,t0 = one_predict(d, delay, dt, Dt)
		if o is None:
			o = tmp
		else:
			Num.minimum(o, tmp, o)
	return o


def local_power(d, dt, Dt):
	return power.smooth(d*d, dt, Dt, extra=WINDOW)


def fractional_step_range(initial, final, step=1):
	"""Generates an array of window offsets.
	No two offsets are equal, and they are integers
	between initial and final."""

	assert step != 0
	if step < 0:
		return fractional_step_range(initial, final, -step)
	if final < initial:
		return []
	o = []
	tmp = float(initial)
	assert tmp > 0.5, "Initial=%g too close to zero, or even negative!" % tmp
	ilast = 0
	while tmp <= final:
		itmp = int(round(tmp))
		if itmp != ilast and itmp>=initial:
			o.append(itmp)
		ilast = itmp
		tmp += step
	return o


def  steady_state(d, dt, Dt):
	if Fmin*dt > 0.5 or Fmin*dt<1.0/d.shape[0]:
		die.warn("Silly time scale")
	die.info("Hipass at %f" % (Fmin*dt))
	d = voice_misc.hipass_sym_butterworth(d, Fmin*dt)
	d = voice_misc.hipass_first_order(d, Fhp*dt)
	if DBG:
		gpkimgclass.gpk_img({'CDELT2': dt}, d).write(DBG)
	p,tshift = local_power(d, dt, Dt)
	assert tshift < Dt
	imin = 1.0/(dt * Fmax)
	imax = 1.0/(dt * Fmin)
	istep = DELTA_DELAY/dt
	delays = fractional_step_range(imin, imax, istep)
	perr = predict_err(d, delays, dt, Dt)
		# The factor of 2.0 below is because perr is a difference
		# of two signals.  If they were independent random noise,
		# then the variances would add, so that perr=2*p for
		# white noise.
		# In other words, this measure goes to 1 for white noise,
		# and to zero for a periodic signal.
	assert perr.shape == p.shape
	return Num.sqrt(perr/(2.0*p))




if __name__ == '__main__':
	import sys

	try:
		import psyco
		psyco.full(memory=10000)
	except ImportError:
		pass

	arglist = sys.argv[1:]
	fname = None
	column = None
	out = "foo.irr.d"
	extrahdr = {}
	while len(arglist)>0 and arglist[0].startswith('-'):
		arg = arglist.pop(0)
		if arg == '--':
			break
		elif arg == '-dt':
			DT = float(arglist.pop(0))
		elif arg == '-f':
			fname = arglist.pop(0)
		elif arg == '-c':
			column = arglist.pop(0)
			try:
				column = int(column)
			except ValueError:
				pass
		elif arg == '-d':
			DBG = arglist.pop(0)
		elif arg == '-o':
			out = arglist.pop(0)
		elif arg == '-write':
			extrahdr = dict( [q.strip().split('=', 1)
					for q in arglist.pop(0).split(';') ]
					)
		else:
			die.info("Unrecognized flag: %s" % arg)
			print __doc__
			die.exit(1)
	d = gpkimgclass.read(fname)
	ss = steady_state(d.column(column), d.dt(), DT)
	hdr = d.hdr.copy()
	hdr['CDELT2'] = DT
	hdr['CRPIX2'] = 0
	hdr['CRVAL2'] = d.start()
	hdr['CDELT1'] = 1
	hdr['TTYPE1'] = 'aperiodicity'
	hdr['BITPIX'] = -32
	hdr.update( extrahdr )
	gpkimgclass.gpk_img(hdr, ss).write(out)
