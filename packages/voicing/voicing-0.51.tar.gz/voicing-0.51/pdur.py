#!/usr/bin/env python

"""Duration estimator for speech.

Usage: s_slope [flags]
Flags: -f FFF opens file FFF for reading.
	-c XXX  selects column XXX (either a data name or an integer).
	-o FFF  sets the output file.
	-dt #.##   Sets the interval for calculating the output.

It takes a local spectrum,
bins it onto the Bark scale,
converts to perceptual loudness (via **E).
Then, it computes a measure of how far you can go
from each point before the spectrum changes too much.
"""

import Num
import math as M
import bark_scale
import die
import gpkmisc

import sys
import os
sys.path.insert(0, os.environ['OXIVOICE'])
import voice_misc



CBmax = bark_scale.f_to_bark(5500.0)
CBmin = bark_scale.f_to_bark(100.0)
BBSZ = 0.5
SPECWINDOW = 0.0546
NORMWINDOW = 0.197
E = 0.333
C = 91.2
RTYPE = 'dur'
LFAC = 1.03
EXP1 = 2
EXP2 = 1

def NEee(x):
	# return Num.log(x)
	return x**E

def iNEee(x):
	return x**(1.0/E)


class bark_bin:
	__doc__ = """This class will bin a power spectrum in uniform frequency bins
		into bins of uniform width on a Bark scale."""

	def __init__(self, df, n2, bbsz, CBmin, CBmax):
		"""Build some arrays so we can bin data rapidly."""
		ctrs = CBmin + bbsz*Num.arrayrange(int(M.ceil((CBmax-CBmin)/bbsz)))
		lbound = bark_scale.bark_to_f(ctrs-0.5)
		assert df > 0.0
		hbound = bark_scale.bark_to_f(ctrs+0.5)
		f = Num.arrayrange(n2) * df
		llb = 0
		lhb = 0
		nf = f.shape[0]
		llba = []
		lhba = []
		correction = []
		for i in range(len(ctrs)):
			llb = int(round(lbound[i]/df))
			lhb = int(round(hbound[i]/df))
			assert lhb > llb
			if lhb >= nf:
				break
			llba.append(llb)
			lhba.append(lhb)
			assert f[lhb] > f[llb]
			correction.append((f[lhb]-f[llb])/(hbound[i]-lbound[i]))
			# This corrects for the fact that the width of each bin is not quite
			# one bark, because the input frequency data is sampled.
		self.llb = Num.array(llba, copy=True)	# Lower bound for a bin
		self.lhb = Num.array(lhba, copy=True)	# Upper bound for a bin.
		self.ctrs = ctrs[:self.llb.shape[0]]
		self.correction = Num.array(correction, copy=True)
		# print 'Bllb', self.llb
		# print 'Blhb', self.lhb
		# print 'Bcor', self.correction
		# print 'Bctr', self.ctrs
		assert Num.alltrue(Num.greater(self.correction, 0.5)*Num.less(self.correction, 2.0))
		assert self.llb.shape == self.lhb.shape
		assert self.llb.shape == self.correction.shape


	def bin(self, pwr):
		"""Do the actual binning.
		Return power in bark scale bins and bin centers.
		Bin centers are in units of barks."""

		# print 'bpwr', pwr
		pwrsum = Num.add.accumulate(pwr)
		# print 'bps', pwrsum
		o = (Num.take(pwrsum, self.lhb) - Num.take(pwrsum, self.llb))/self.correction
		# print 'bo', o
		assert Num.alltrue( Num.greater_equal(o, 0.0) )
		assert o.shape == self.ctrs.shape
		# return (o**E, self.ctrs)
		return (o, self.ctrs)


_bbc = {}
def bark_bin_cached(df, n2, bbsz, CBmin, CBmax):
	key = (df, n2, bbsz, CBmin, CBmax)
	if key not in _bbc:
		if len(_bbc) > 20:
			_bbc.popitem()
		_bbc[key] = bark_bin(df, n2, bbsz, CBmin, CBmax)
	return _bbc[key]



def _log_it(name, *d):
	fd = open(name, "w")
	n = d[0].shape
	for tmp in d:
		assert tmp.shape == n
	for i in range(n[0]):
		for tmp in d:
			fd.write("%g " % tmp[i])
		fd.write('\n')
	fd.close()



def one_spec_guts(d, extra):
	"""Approximate spectral slope of the sound in data array d.
	Extra contains misc. parameters."""

	n = d.shape[0]
	die.note("n", n)
	assert d.shape == (n,)
	df = 1/(n*extra['dt'])
	# print "# n=", n, "df=", df
	# print 'd=', d
	# print 'misc_win', voice_misc.window(n, 0)
	ss = Num.FFT.fft( d*voice_misc.window(n, 0) )
	ss[0] = 0	# Remove DC offset.
	pwr = Num.absolute(ss)**2/n
	bbin = bark_bin_cached(df, n/2, BBSZ, CBmin, CBmax)
	barkpwr, fbark = bbin.bin(pwr[:n/2])
	# print 'pwr=', Num.sum(pwr), Num.sum(barkpwr)

	return NEee(barkpwr)


def one_spec_norm(d):
	assert len(d.shape) == 1
	w = voice_misc.window(d.shape[0], 0)
	return M.sqrt(Num.sum((w*d)**2))	# Num.sum(w**2)==1


def one_spec(t, data, extra):
	"""Measure the spectrum near time t*DT.
	It returns a normalized spectrum and the normalization factor.
	"""
	# print 't=', t, 'DT=', extra['DT'], 'dt=', extra['dt']
	if extra.has_key('column'):
		extra['logname'] = "%st%d" % (extra['column'], t)
	tdt = t*extra['DT']
	s, e = voice_misc.start_end(tdt, extra['dt'],
					extra['window'], data.shape[0])
	ns, ne = voice_misc.start_end(tdt, extra['dt'],
					int(round(NORMWINDOW/dt)), data.shape[0])
	# print 's, e=', s, e, ns, ne, norm
	n1 = one_spec_norm(data[ns:ne])
	d = data[s:e]/n1
	return (one_spec_guts(d, extra), n1)



def spec(data, extra):
	"""Measure the time-series of the spectrum of a data array data.
	DT is the sampling interval for the resulting time series.
	It returns an array (s,norm) where s is the normalized spectra
	and norm is the time series of the normalized power.
	s[t,f] is the normalized power density at time t and frequency f.
	norm[t] is proportional to the power near time t."""

	ns = int(round(extra['dt']*data.shape[0]/extra['DT']))
	so = None
	no = Num.zeros((ns,), Num.Float)
	for t in range(ns):
		# t is measured relative to the beginning of the data.
		s,n = one_spec(t, data, extra)
		if so is None:
			so = Num.zeros((ns,s.shape[0]), Num.Float)
		so[t,:] = s
		no[t] = n
	return (so, no)



def calc_prelims(dt, Dt):
	extra = {'dt': dt, 'DT': Dt}
	extra['window'] = voice_misc.near_win_size(near=SPECWINDOW/dt, tol=0.1*SPECWINDOW/dt)
	return extra


def pdur_guts(s, t, dir, Dt):
	"""t is an integer; an index into the data.
	S is the normalized perceptual spectrum."""
	n = len(s)
	sumdiff = 0.0
	len_sum = 0.5	# The integral for the i==t case is trivial.
	ctr_sum = 0.125*dir	# The integral for i==t is trivial.
	i = t + dir
	while i>=0 and i<n and sumdiff<8:
		delta_diff = Dt * C * Num.sum( Num.absolute(s[i]-s[t])**EXP1 )**EXP2

		# We assume that the spectrum is s[i] in the
		# region from i-0.5 to i+0.5, and compute the
		# integral( M.exp(-integral((s(t0)-s(t''))**2 from 0 to t', dt''))
		# 	from 0 to i+0.5, dt')
		# The constancy of s over the interval (i-0.5,i+0.5)
		# makes the inner integral piecewise linear.
		# Sumdiff holds integral((s(t0)-s(t''))**2 from 0 to i-0.5)
		if delta_diff <= 0:
			# assume delta_diff = 0
			lsd = M.exp(-sumdiff)
			len_sum += lsd
			# integral( (t''-t0)*M.exp(-integral((s(t0)-s(t''))**2 from 0 to t', dt''))
			# 	from 0 to i+0.5, dt')
			slopeint = M.exp(-sumdiff) * 0.5
			ctr_sum += (i-t-0.5*dir)*lsd + dir * slopeint
			i += dir
		else:
			lsd = M.exp(-sumdiff) * (1.0-M.exp(-delta_diff))/delta_diff
			len_sum += lsd
			# integral( (t''-t0)*M.exp(-integral((s(t0)-s(t''))**2 from 0 to t', dt''))
			# 	from 0 to i+0.5, dt')
			slopeint = M.exp(-sumdiff)	\
					* (1.0-M.exp(-delta_diff)*(1+delta_diff))/delta_diff**2
			ctr_sum += (i-t-0.5*dir)*lsd + dir * slopeint
			i += dir
			sumdiff += delta_diff
		# Now, sumdiff holds integral((s(t0)-s(t''))**2 from 0 to i+0.5)
	# print 't=', t, sum
	return (len_sum*Dt, ctr_sum*Dt)


def pdur(data, extra, out):
	extra.update( calc_prelims(dt, Dt=DT))
	# print 's.n=', data.shape
	data = data - gpkmisc.N_median(data)
	data = data / M.sqrt(Num.sum( data**2 )/data.shape[0])
	sp,np = spec(data, extra)
	print 'sps=', sp.shape
	AvNormPwr = Num.sum(Num.ravel(iNEee(sp)))/sp.shape[0]
	print '# AvNormPwr=', AvNormPwr
	assert 0.03 <= AvNormPwr <= 10.0

	ns = sp.shape[0]
	o = Num.zeros((ns,), Num.Float)
	for i in range(ns):
		plp, pcp = pdur_guts(sp, i, 1, extra['DT'])
		plm, pcm = pdur_guts(sp, i, -1, extra['DT'])
		if out=='dur':
			o[i] = LFAC * (plp + plm)
		elif out=='center':
			o[i] = extra['DT']*(pcp + pcm)/(plp+plm)
		else:
			die.die('Whoops')
	return o
	


if __name__ == '__main__':
	import gpkimgclass
	try:
		import psyco
		psyco.full()
	except ImportError:
		pass

	DT = 0.01	# Seconds.  Default output sampling interval.
	arglist = sys.argv[1:]
	column = None
	signalfile = None
	outfile = None
	extrahdr = {}
	while len(arglist)>0 and arglist[0][0]=='-':
		arg = arglist.pop(0)
		if arg == '-c':
			assert column is None
			tmp = arglist.pop(0)
			try:
				column = int( tmp )
			except ValueError:
				column = tmp
		elif arg == '-f':
			signalfile = arglist.pop(0)
			die.note("signalfile", signalfile)
		elif arg == '-normwin':
			NORMWINDOW = float(arglist.pop(0))
			assert NORMWINDOW > 0
		elif arg == '-lfac':
			LFAC = M.exp(float(arglist.pop(0)))
		elif arg == '-specwin':
			SPECWINDOW = float(arglist.pop(0))
			assert SPECWINDOW > 0
		elif arg == '-exp1':
			EXP1 = float(arglist.pop(0))
			assert EXP1 > 0
		elif arg == '-exp2':
			EXP2 = float(arglist.pop(0))
			assert EXP2 > 0
		elif arg == '-C':
			C = float(arglist.pop(0))
		elif arg == '-o':
			outfile = arglist.pop(0)
		elif arg == '-dt':
			DT = float(arglist.pop(0))
		elif arg == '-dur':
			RTYPE = 'dur'
		elif arg == '-ctr':
			RTYPE = 'center'
		elif arg == '-fmax':
			CBmax = bark_scale.f_to_bark(float(arglist.pop(0)))
		elif arg == '-fmin':
			CBmin = bark_scale.f_to_bark(float(arglist.pop(0)))
		elif arg == '-write':
			extrahdr = dict( [q.strip().split('=', 1)
					for q in arglist.pop(0).split(';') ]
					)
		else:
			die.info("Unrecognized flag: %s" % arg)
			print __doc__
			die.exit(1)
	if len(arglist) > 0:
		rootname = arglist.pop(0)
		if signalfile == None:
			signalfile = rootname + '.d'
		if outfile == None:
			outfile = rootname + '.pdur.dat'
	if outfile is None:
		outfile = 'pdur.dat'
	if signalfile is None:
		die.info("No signal file specified.")
		print __doc__
		die.exit(1)
	signal = gpkimgclass.read(signalfile)
	nch = signal.d.shape[1]
	try:
		signal.column(column)
	except KeyError:
		die.info("File has %d columns" % signal.n[1])
		die.die("Bad column: %s" % str(column))

	dt = signal.dt()
	extra = {}

	print "#column=", column
	try:
		o = pdur(signal.column(column), extra, RTYPE)
	except:
		die.warn("Exception in pdur calculation")
		raise

	hdr = signal.hdr.copy()
	hdr['CDELT2'] = DT
	hdr['CRPIX2'] = 0
	hdr['CRVAL2'] = signal.start()
	hdr['CDELT1'] = 1
	hdr['TTYPE1'] = 'pseudoduration'
	hdr['BITPIX'] = -32
	hdr.update( extrahdr )
	oo = gpkimgclass.gpk_img(hdr, o)
	oo.write(outfile)


