#!/usr/bin/env python

"""RMS or peak amplitude time series."""


import Num
import math
import die

import sys
import os
sys.path.insert(0, os.environ['OXIVOICE'])
import voice_misc
import power
# import is_voiced



DR = 'rms'
DTSMOOTH = 0.015
DT = 0.01	# Seconds.  Default output sampling interval.
HPF = 40.0	# Hz
PKWDT = 0.020	# Full-width of window for computing peak amplitude.




def one_pk_pk(t, data, dt, DT):
	"""Measure the loudness near time t."""
	s, e = voice_misc.start_end(t*DT, dt, int(round(PKWDT/dt)), data.shape[0])
	d = data[s:e]
	return d[ Num.argmax( d ) ] - d[ Num.argmin(d) ]


def compute_intensity(data, dt, DT, DR, HPF, DTSmooth=DTSMOOTH):
	"""Measure the time-series of RMS of a data array data.
	DT is the sampling interval for the resulting RMS time series."""
	if HPF is not None:
		data = voice_misc.hipass_sym_butterworth(data, HPF*dt)
	if DR == 'rms':
		pwr, t0 = power.smooth(data**2, dt, DT, DTSmooth)
		rms = Num.sqrt(pwr)
	elif DR == 'avd':
		rms,t0 = power.smooth(Num.absolute(data), dt, DT, DTSmooth)
	elif DR == 'pkpk':
		ns = int(math.floor(data.shape[0]*(dt/DT)))
		# print 'ns=', dt, data.shape[0], DT, dt*data.shape[0]/DT
		pkpk = Num.zeros((ns,), Num.Float)
		for t in range(ns):
			pkpk[t] = one_pk_pk(t, data, dt, DT)
		rms,t0 = power.smooth(pkpk, DT, DT, DTSmooth)
	else:
		die('Bad DR=%s' % DR)
	return (rms,t0)



if __name__ == '__main__':
	import gpkimgclass
	arglist = sys.argv[1:]
	columns = None
	signalfile = None
	outfile = None
	extrahdr = {}
	while len(arglist)>0 and arglist[0][0]=='-':
		arg = arglist.pop(0)
		if arg == '-c':
			if columns == None:
				columns = []
			tmp = arglist.pop(0)
			try:
				col = int(tmp)
			except ValueError:
				col = tmp
			columns.append(col)
		elif arg == '-pkpk':
			DR = 'pkpk'
		elif arg == '-f':
			signalfile = arglist.pop(0)
			die.note("signalfile", signalfile)
		elif arg == '-o':
			outfile = arglist.pop(0)
		elif arg == '-dt':
			DT = float(arglist.pop(0))
			assert DT>0.0, 'Silly time step.'
		elif arg == '-hpf':
			HPF = float(arglist.pop(0))
			assert HPF > 0.0, "Silly highpass frequency"
		elif arg == '-write':
			extrahdr = dict( [q.strip().split('=', 1)
					for q in arglist.pop(0).split(';') ]
					)
		else:
			die.die("Unrecognized flag: %s" % arg)
	if len(arglist) > 0:
		rootname = arglist.pop(0)
		if signalfile == None:
			signalfile = rootname + '.d'
		if outfile == None:
			outfile = '%s.%s.dat' % (rootname, DR)
	if outfile == None:
		outfile = '%s.dat' % DR
	signal = gpkimgclass.read(signalfile)
	nch = signal.d.shape[1]
	if columns == None:
		columns = range(nch)
	die.note("columns", str(columns))
	for c in columns:
		try:
			signal.column(c)
		except KeyError:
			die.info("File has %d columns" % signal.n[1])
			die.die("Bad column: %s" % str(c))

	tmp = []
	t00 = None
	for i in columns:
		tmpR, t0 = compute_intensity(signal.column(i), signal.dt(), DT, DR, HPF)
		tmp.append( tmpR )
		if t00 == None:
			t00 = t0
		else:
			assert abs(t00-t0)/DT < 0.001
	n = len(tmp[0])
	o = Num.zeros((n,), Num.Float)
	for t in tmp:
		Num.add(o, t, o)
	o = o / nch

	hdr = signal.hdr.copy()
	hdr['CDELT2'] = DT
	hdr['CRPIX2'] = 0
	hdr['CRVAL2'] = signal.start() + t0
	hdr['CDELT1'] = 1
	hdr['TTYPE1'] = DR
	hdr['BITPIX'] = -32
	hdr.update( extrahdr )
	oo = gpkimgclass.gpk_img(hdr, Num.transpose( [o]))
	oo.write(outfile)

