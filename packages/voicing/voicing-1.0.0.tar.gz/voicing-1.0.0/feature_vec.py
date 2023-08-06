#!/usr/bin/env python


import erb_scale
import Num
import die
import math
import avio
import gpkmisc
import sets

import os
import sys
sys.path.insert(0, os.environ['OXIVOICE'])
import percep_spec
import voice_misc
# import irregularity
# sys.path.insert(0, '%s/tick1/bin' % os.environ['MRImodel'])

if 'PYLABDISP' in os.environ:
	if os.environ['PYLABDISP'] == 'pylab':
		import pylab
	else:
		import g_pylab as pylab
	PLOT = True
else:
	PLOT = False

if False:
	def edgepair_win(n):
		e = Num.zeros((2*n,), Num.Float)
		e[:n] = -1.0
		e[n:] = 1.0
		s = Num.ones((2*n), Num.Float)
		return (e, s)
else:
	def edgepair_win(n):
		tmp0 = voice_misc.window(2*n, 0)
		tmp1 = voice_misc.window(2*n, 1)
		norm = gpkmisc.N_maximum(tmp0)
		return (tmp1/norm, tmp0/norm)


if False:
	def win(n):
		tmp = Num.ones((n,), Num.Float)
		return tmp
else:
	def win(n):
		tmp = voice_misc.window(n, 0)
		return tmp/gpkmisc.N_maximum(tmp)


def burst_win(n, i):
	tmp = Num.zeros((n,), Num.Float)
	tmp[i] = 1.0
	neg = win(n)
	nneg = neg/Num.sum(neg)
	return (tmp - nneg, nneg)


def entropy(w):
	assert Num.alltrue( Num.greater(w, 0.0) )
	p = w/Num.sum(w)
	return -Num.sum(p*Num.log(p))



# SpecExp = 0.0
NSV = 0.75
Dt = 0.005
DB = math.sqrt(0.5)
Lf = 1.5
Elf = 1.5
# Nsv and LF updated from the 5 April 2007 optimization
# in .../m/ASR/OPT

def feature_vec(data, dt, DT=Dt,
		LF=1.0, Nsv=NSV, ELF=1.0,
		do_voicing=True, do_dissonance=True,
		PlompBouman=False):
	FORMANT_LOW = erb_scale.f_to_erb(60.0)
	FORMANT_HIGH = erb_scale.f_to_erb(6000.0)
	assert DT > 0.0 and float(DT)>0.0
	assert LF > 0.0 and float(LF)>0.0
	bmin = erb_scale.f_to_erb(80.0)
	bmax = erb_scale.f_to_erb(7000.0)
	all_ectrs, all_ps, t0 = percep_spec.perceptual_spec(data, dt, DT,
							bmin, bmax, DB,
							do_mod=do_voicing,
							do_dissonance=do_dissonance,
							PlompBouman=PlompBouman
							)

	band_indices = [i for (i,ec) in enumerate(all_ectrs) if ec['type']=='band']
	neural = all_ps.take(band_indices, axis=0)
	ectrs = [ec for ec in all_ectrs if ec['type']=='band']
	nband_indices = [i for (i,ec) in enumerate(all_ectrs) if ec['type']!='band']
	nneural = all_ps.take(nband_indices, axis=0)
	nectrs = [ec for ec in all_ectrs if ec['type']!='band']

	assert nneural.shape[1]==neural.shape[1]
	assert neural.shape[1]==all_ps.shape[1]
	assert neural.shape[0]+nneural.shape[0] == all_ps.shape[0]

	neural_now = Num.average(neural, axis=0)	# Average over frequency.
	assert neural_now.shape[0] == neural.shape[1]
	neural_avg = Num.sum(neural_now**2)/Num.sum(neural_now)	# Average over time.
		# neural_avg is a scalar, grand average.
	Num.divide(neural, neural_avg, neural)
		# Now, we've normalized by an over-all average loudness.
	Num.divide(neural_now, neural_avg, neural_now)
		# Now, we've normalized by an over-all average loudness.

	assert nneural.shape[0] < nneural.shape[1]
	assert len(nectrs) == nneural.shape[0]
	for (i,e) in enumerate(nectrs):
		if e['type'] == 'haspitch':
			Num.divide(nneural[i,:], neural_avg, nneural[i,:])
		if e['type'] == 'dissonance':
			Num.divide(nneural[i,:], neural_avg, nneural[i,:])

	# print '# neural_avg=', neural_avg
	o = []
	descr = []
	wset = sets.Set([0])
	for vl in [0.01]:
		# print 'vl=', vl, type(vl), 'LF=', LF, type(LF), 'DT=', DT, type(DT)
		w = int(round(vl*LF/DT))
		if not w in wset:
			tmpo, tmpd = vowel(w, ectrs, neural, neural_now, Nsv,
						formant_low=FORMANT_LOW,
						formant_high=FORMANT_HIGH
						)
			o.extend(tmpo)
			descr.extend(tmpd)
			wset.add(w)

	wset = sets.Set([0])
	for fel in [0.06]:
		w = int(round(fel*ELF/DT))
		if not w in wset:
			tmpo, tmpd = fricative_edge(ectrs, neural, neural_now, Nsv,
						do_abs=False, width=w
						)
			o.extend(tmpo)
			descr.extend(tmpd)
			wset.add(w)

	wset = sets.Set([0])
	for sel in [0.01]:
		w = int(round(sel*LF/DT))
		if not w in wset:
			tmpo, tmpd = spectral_entropy(w, ectrs, neural, neural_now, Nsv)
			o.extend(tmpo)
			descr.extend(tmpd)
			wset.add(w)
		assert len(descr)==len(o), "Descriptor mismatch"


	if do_voicing:
		wset = sets.Set([0])
		for hpl in [0.06]:
			w = int(round(hpl*LF/DT))
			if not w in wset:
				tmpo, tmpd = haspitch(w, nectrs, nneural, neural_now, Nsv)
				o.extend(tmpo)
				descr.extend(tmpd)
				wset.add(w)
	if do_dissonance:
		wset = sets.Set([0])
		for dsl in [0.06]:
			w = int(round(dsl*LF/DT))
			if not w in wset:
				tmpo, tmpd = dissonance(w, nectrs, nneural, neural_now, Nsv)
				o.extend(tmpo)
				descr.extend(tmpd)
				wset.add(w)

	assert len(descr)==len(o), "Descriptor mismatch"
	N = neural[0].shape[0]
	for (i, (tmp, dsc)) in enumerate(zip(o, descr)):
		assert tmp.shape == (N,), "Wrong size: %d, %s = %d vs. %d" % (i, str(dsc), tmp.shape[0], N)

	return (o, descr, DT, t0)



def feature_vec20071030(data, dt, DT=Dt,
		LF=1.0, Nsv=NSV,
		ELF=1.0,
		do_voicing=True, do_dissonance=True):
	FORMANT_LOW = erb_scale.f_to_erb(60.0)
	FORMANT_HIGH = erb_scale.f_to_erb(5000.0)
	assert DT > 0.0 and float(DT)>0.0
	assert LF > 0.0 and float(LF)>0.0
	bmin = erb_scale.f_to_erb(80.0)
	bmax = erb_scale.f_to_erb(7000.0)
	all_ectrs, all_ps, t0 = percep_spec.perceptual_spec(data, dt, DT,
							bmin, bmax, DB,
							do_mod=do_voicing,
							do_dissonance=do_dissonance,
							PlompBouman=True
							)

	band_indices = [i for (i,ec) in enumerate(all_ectrs) if ec['type']=='band']
	neural = all_ps.take(band_indices, axis=0)
	ectrs = [ec for ec in all_ectrs if ec['type']=='band']
	nband_indices = [i for (i,ec) in enumerate(all_ectrs) if ec['type']!='band']
	nneural = all_ps.take(nband_indices, axis=0)
	nectrs = [ec for ec in all_ectrs if ec['type']!='band']

	assert nneural.shape[1]==neural.shape[1]
	assert neural.shape[1]==all_ps.shape[1]
	assert neural.shape[0]+nneural.shape[0] == all_ps.shape[0]

	neural_now = Num.average(neural, axis=0)	# Average over frequency.
	assert neural_now.shape[0] == neural.shape[1]
	neural_avg = Num.sum(neural_now**2)/Num.sum(neural_now)	# Average over time.
		# neural_avg is a scalar, grand average.
	Num.divide(neural, neural_avg, neural)
		# Now, we've normalized by an over-all average loudness.
	Num.divide(neural_now, neural_avg, neural_now)
		# Now, we've normalized by an over-all average loudness.

	assert nneural.shape[0] < nneural.shape[1]
	assert len(nectrs) == nneural.shape[0]
	for (i,e) in enumerate(nectrs):
		if e['type'] == 'haspitch':
			Num.divide(nneural[i,:], neural_avg, nneural[i,:])
		if e['type'] == 'dissonance':
			Num.divide(nneural[i,:], neural_avg, nneural[i,:])

	# print '# neural_avg=', neural_avg
	o = []
	descr = []
	wset = sets.Set([0])
	for vl in [0.04]:
		# print 'vl=', vl, type(vl), 'LF=', LF, type(LF), 'DT=', DT, type(DT)
		w = int(round(vl*LF/DT))
		if not w in wset:
			tmpo, tmpd = vowel(w, ectrs, neural, neural_now, Nsv,
						formant_low=FORMANT_LOW,
						formant_high=FORMANT_HIGH
						)
			o.extend(tmpo)
			descr.extend(tmpd)
			wset.add(w)

	wset = sets.Set([0])
	for fel in [0.06]:
		w = int(round(fel*ELF/DT))
		if not w in wset:
			tmpo, tmpd = fricative_edge(ectrs, neural, neural_now, Nsv,
						do_abs=False, width=w
						)
			o.extend(tmpo)
			descr.extend(tmpd)
			wset.add(w)

	wset = sets.Set([0])
	for sel in [0.04]:
		w = int(round(sel*LF/DT))
		if not w in wset:
			tmpo, tmpd = spectral_entropy(w, ectrs, neural, neural_now, Nsv)
			o.extend(tmpo)
			descr.extend(tmpd)
			wset.add(w)
		assert len(descr)==len(o), "Descriptor mismatch"


	if do_voicing:
		wset = sets.Set([0])
		for hpl in [0.05]:
			w = int(round(hpl*LF/DT))
			if not w in wset:
				tmpo, tmpd = haspitch(w, nectrs, nneural, neural_now, Nsv)
				o.extend(tmpo)
				descr.extend(tmpd)
				wset.add(w)
	if do_dissonance:
		wset = sets.Set([0])
		for dsl in [0.05]:
			w = int(round(dsl*LF/DT))
			if not w in wset:
				tmpo, tmpd = dissonance(w, nectrs, nneural, neural_now, Nsv)
				o.extend(tmpo)
				descr.extend(tmpd)
				wset.add(w)

	assert len(descr)==len(o), "Descriptor mismatch"
	N = neural[0].shape[0]
	for (i, (tmp, dsc)) in enumerate(zip(o, descr)):
		assert tmp.shape == (N,), "Wrong size: %d, %s = %d vs. %d" % (i, str(dsc), tmp.shape[0], N)

	return (o, descr, DT, t0)



def simple_feature_vec(data, dt, DT=Dt,
		LF=1.0, Nsv=NSV, ELF=None,
		do_voicing=True, do_dissonance=True, PlompBouman=True):
	FORMANT_LOW = erb_scale.f_to_erb(60.0)
	FORMANT_HIGH = erb_scale.f_to_erb(6000.0)
	assert DT > 0.0 and float(DT)>0.0
	assert LF > 0.0 and float(LF)>0.0
	bmin = erb_scale.f_to_erb(80.0)
	bmax = erb_scale.f_to_erb(7000.0)
	all_ectrs, all_ps, t0 = percep_spec.perceptual_spec(data, dt, DT,
							bmin, bmax, DB,
							do_mod=do_voicing,
							do_dissonance=do_dissonance,
							PlompBouman=PlompBouman
							)

	band_indices = [i for (i,ec) in enumerate(all_ectrs) if ec['type']=='band']
	# print 'band_indices=', band_indices
	neural = all_ps.take(band_indices, axis=0)
	ectrs = [ec for ec in all_ectrs if ec['type']=='band']
	# print 'ectrs=', ectrs
	nband_indices = [i for (i,ec) in enumerate(all_ectrs) if ec['type']!='band']
	# print 'nband_indices=', nband_indices
	nneural = all_ps.take(nband_indices, axis=0)
	nectrs = [ec for ec in all_ectrs if ec['type']!='band']
	# print 'nectrs=', nectrs

	assert nneural.shape[1]==neural.shape[1]
	assert neural.shape[1]==all_ps.shape[1]
	assert neural.shape[0]+nneural.shape[0] == all_ps.shape[0]

	neural_now = Num.average(neural, axis=0)
	# pylab.plot(neural_now)
	# pylab.title('neural_now')
	# pylab.show()
	assert neural_now.shape[0] == neural.shape[1]
	neural_avg = Num.sum(neural_now**2)/Num.sum(neural_now)
	# print 'neural_avg=', neural_avg
	Num.divide(neural, neural_avg, neural)
	Num.divide(neural_now, neural_avg, neural_now)
	# pylab.plot(neural_now)
	# pylab.title('normed neural_now')
	# pylab.show()

	assert nneural.shape[0] < nneural.shape[1]
	assert len(nectrs) == nneural.shape[0]
	for (i,e) in enumerate(nectrs):
		if e['type'] == 'haspitch':
			Num.divide(nneural[i,:], neural_avg, nneural[i,:])
		if e['type'] == 'dissonance':
			Num.divide(nneural[i,:], neural_avg, nneural[i,:])

	# print '# neural_avg=', neural_avg
	o = []
	descr = []
	tmpo, tmpd = vowel(1, ectrs, neural, neural_now, Nsv,
						formant_low=FORMANT_LOW,
						formant_high=FORMANT_HIGH
						)
	o.extend(tmpo)
	descr.extend(tmpd)
	assert len(descr)==len(o), "Descriptor mismatch"

	tmpo, tmpd = spectral_entropy(1, ectrs, neural, neural_now, Nsv)
	o.extend(tmpo)
	descr.extend(tmpd)
	assert len(descr)==len(o), "Descriptor mismatch"


	if do_voicing:
		Hpl = 0.03
		w = int(round(Hpl*LF/DT))
		tmpo, tmpd = haspitch(w, nectrs, nneural, neural_now, Nsv)
		o.extend(tmpo)
		descr.extend(tmpd)

	if do_dissonance:
		Dsl = 0.04
		w = int(round(Dsl*LF/DT))
		tmpo, tmpd = dissonance(w, nectrs, nneural, neural_now, Nsv)
		o.extend(tmpo)
		descr.extend(tmpd)

	assert len(descr)==len(o), "Descriptor mismatch"
	N = neural[0].shape[0]
	for (i, (tmp, dsc)) in enumerate(zip(o, descr)):
		assert tmp.shape == (N,), "Wrong size: %d, %s = %d vs. %d" % (i, str(dsc), tmp.shape[0], N)

	return (o, descr, DT, t0)



def ss_feature_vec(data, dt, DT=Dt,
		LF=1.0, Nsv=NSV, ELF=None,
		do_voicing=True, do_dissonance=False, PlompBouman=True):
	FORMANT_LOW = erb_scale.f_to_erb(200.0)
	FORMANT_HIGH = erb_scale.f_to_erb(4000.0)
	assert DT > 0.0 and float(DT)>0.0
	assert LF > 0.0 and float(LF)>0.0
	bmin = erb_scale.f_to_erb(100.0)
	bmax = erb_scale.f_to_erb(6000.0)
	all_ectrs, all_ps, t0 = percep_spec.perceptual_spec(data, dt, DT,
							bmin, bmax, DB,
							do_mod=True,
							do_dissonance=False,
							PlompBouman=PlompBouman
							)

	band_indices = [i for (i,ec) in enumerate(all_ectrs) if ec['type']=='band']
	# print 'band_indices=', band_indices
	neural = all_ps.take(band_indices, axis=0)
	ectrs = [ec for ec in all_ectrs if ec['type']=='band']
	# print 'ectrs=', ectrs
	nband_indices = [i for (i,ec) in enumerate(all_ectrs) if ec['type']!='band']
	# print 'nband_indices=', nband_indices
	nneural = all_ps.take(nband_indices, axis=0)
	nectrs = [ec for ec in all_ectrs if ec['type']!='band']
	# print 'nectrs=', nectrs

	assert nneural.shape[1]==neural.shape[1]
	assert neural.shape[1]==all_ps.shape[1]
	assert neural.shape[0]+nneural.shape[0] == all_ps.shape[0]

	neural_now = Num.average(neural, axis=0)
	# pylab.plot(neural_now)
	# pylab.title('neural_now')
	# pylab.show()
	assert neural_now.shape[0] == neural.shape[1]
	neural_avg = Num.sum(neural_now**2)/Num.sum(neural_now)
	# print 'neural_avg=', neural_avg
	Num.divide(neural, neural_avg, neural)
	Num.divide(neural_now, neural_avg, neural_now)
	# pylab.plot(neural_now)
	# pylab.title('normed neural_now')
	# pylab.show()

	assert nneural.shape[0] < nneural.shape[1]
	assert len(nectrs) == nneural.shape[0]
	for (i,e) in enumerate(nectrs):
		if e['type'] == 'haspitch':
			Num.divide(nneural[i,:], neural_avg, nneural[i,:])
		if e['type'] == 'dissonance':
			Num.divide(nneural[i,:], neural_avg, nneural[i,:])

	# print '# neural_avg=', neural_avg
	o = []
	descr = []
	Vl = 0.06
	w = int(round(Vl*LF/DT))
	tmpo, tmpd = vowel(w, ectrs, neural, neural_now, Nsv,
						formant_low=FORMANT_LOW,
						formant_high=FORMANT_HIGH
						)
	o.extend(tmpo)
	descr.extend(tmpd)
	assert len(descr)==len(o), "Descriptor mismatch"

	if not do_voicing:
		raise RuntimeError, "Assumes voicing=True"
	if do_dissonance:
		raise RuntimeError, "Assumes dissonance=False"

	Hpl = 0.07
	w = int(round(Hpl*LF/DT))
	tmpo, tmpd = haspitch(w, nectrs, nneural, neural_now, Nsv)
	o.extend(tmpo)
	descr.extend(tmpd)

	assert len(descr)==len(o), "Descriptor mismatch"
	N = neural[0].shape[0]
	for (i, (tmp, dsc)) in enumerate(zip(o, descr)):
		assert tmp.shape == (N,), "Wrong size: %d, %s = %d vs. %d" % (i, str(dsc), tmp.shape[0], N)

	return (o, descr, DT, t0)


def isfloat(x):
	return isinstance(x, float)


def convolve(signal, kernel):
	"""Returns something the length of the signal, by zero padding."""
	if signal.shape[0] > kernel.shape[0]:
		return Num.convolve(signal, kernel, 1)
	m = 1+kernel.shape[0]-signal.shape[0]
	tmp = Num.concatenate((signal, Num.zeros((m,), Num.Float)))
	die.info('Narrow signal: padding from %d to %d' % (signal.shape[0], m))
	return Num.convolve(tmp, kernel, 1)[:signal.shape[0]]


def vowel(width, ectrs, neural, neural_now, Nsv,
		formant_low=None, formant_high=None):
	VFAC = 0.75
	cs = win(width)
	css = Num.sum(cs)
	nns = convolve(neural_now, cs)/Num.sum(cs)
	norm = Num.hypot(nns, Nsv * Num.sum(nns**2)/Num.sum(nns))
	# The second term within the hypot() should always be Nsv*one.

	# pylab.plot(norm)
	# pylab.figure()
	o = []
	descr = []
	for (i, e) in enumerate(ectrs):
		if e['type']=='band' and formant_low < e['erb'] < formant_high:
			tmp = (VFAC/css)*convolve(neural[i], cs)/norm
			# pylab.plot(tmp)
			o.append(tmp)
			# print 'RMS', math.sqrt(Num.sum(tmp**2)/tmp.shape[0])
			dtmp = e.copy()
			dtmp['type'] = 'vowel'
			dtmp['width'] = width
			dtmp['Kentropy'] = entropy(cs)
			dtmp['Fentropy'] = 0.0
			dtmp['id'] = 'vowel:%d:%.1f' % (width, e['erb'])
			# pylab.title('vowel %s' % dtmp['id'])
			# pylab.figure()
			descr.append( dtmp )
	# pylab.show()
	return (o, descr)


def spectral_entropy(width, ectrs, neural, neural_now, Nsv):
	"""This is inspired (but only loosely) by
	"Robust Entropy-based Endpoint Detection for Speech Recognition
	in Noisy Environments." by Jia-lin Shen and Jeih-weih Hung
	and Lin-shan Lee, http://www.ee.columbia.edu/~dpwe/papers/ShenHL98-endpoint.pdf
	International Conference on Spoken Language Processing, 1998.
	"""
	assert Nsv > 0.0
	SEF = 0.5
	EPS = 1e-10
	cs = win(width)
	assert Num.alltrue( Num.greater(cs, 0.0) )
	css = Num.sum(cs)
	nns = convolve(neural_now, cs)/css
	norm = Num.hypot(nns, Nsv * Num.sum(nns**2)/Num.sum(nns))
	assert Num.alltrue( Num.greater(norm, 0.0) )
	# pylab.plot(norm)
	# pylab.figure()

	ent_sum = None
	np = 0
	Ne = len(ectrs)
	for (i, e) in enumerate(ectrs):
		if e['type']=='band':
			assert Num.alltrue( Num.greater_equal(neural[i], 0.0) )
			ptmp = ((1.0+Nsv)/(Ne*css)) * convolve(neural[i], cs)/norm
			# pylab.plot(ptmp)
			tmp = ptmp * Num.log(ptmp+EPS)
			if ent_sum is None:
				ent_sum = Num.array(tmp, copy=True)
			else:
				Num.add(ent_sum, tmp, ent_sum)
			np += 1

	# pylab.title('spectral_entropy')
	# pylab.show()
	assert np > 0
	dtmp = {'type': 'spectral_entropy',
		'width': width,
		'Kentropy': entropy(cs),
		'Fentropy': math.log(np),
		'id': 'entropy:%d' % width
		}
	EFAC = -0.4
	es0 = EFAC*math.log(np)
	return ([-SEF*(ent_sum-es0)], [dtmp])



def haspitch(width, ectrs, neural, neural_now, Nsv):
	HFAC = {2: 0.08, 1: 0.28}
	cs = win(width)
	css = Num.sum(cs)
	nns = convolve(neural_now, cs)/Num.sum(cs)
	norm = Num.hypot(nns, Nsv * Num.sum(nns**2)/Num.sum(nns))
	o = []
	descr = []
	for (i, e) in enumerate(ectrs):
		if e['type'].startswith('haspitch'):
			tmp = (HFAC[e['variant']]/css)*convolve(neural[i], cs)/norm
			# pylab.figure()
			# pylab.title('e=%s' % e['id'])
			# pylab.plot(neural[i])
			# pylab.plot(tmp)
			# pylab.plot(norm)
			o.append(tmp)
			# print 'RMS', math.sqrt(Num.sum(tmp**2)/tmp.shape[0])
			dtmp = e.copy()
			dtmp['id'] = '%s:%d' % (dtmp['id'], width)
			dtmp['Kentropy'] = entropy(cs)
			assert 'Fentropy' in dtmp
			dtmp['width'] = width
			descr.append( dtmp )
	# pylab.show()
	return (o, descr)


def dissonance(width, ectrs, neural, neural_now, Nsv):
	HFAC = {1: 0.2}
	cs = win(width)
	css = Num.sum(cs)
	nns = convolve(neural_now, cs)/Num.sum(cs)
	norm = Num.hypot(nns, Nsv * Num.sum(nns**2)/Num.sum(nns))
	o = []
	descr = []
	for (i, e) in enumerate(ectrs):
		if e['type'].startswith('dissonance'):
			tmp = (HFAC[e['variant']]/css)*convolve(neural[i], cs)/norm
			# pylab.figure()
			# pylab.title('e=%s' % e['id'])
			# pylab.plot(neural[i])
			# pylab.plot(tmp)
			# pylab.plot(norm)
			o.append(tmp)
			# print 'RMS', math.sqrt(Num.sum(tmp**2)/tmp.shape[0])
			dtmp = e.copy()
			dtmp['id'] = '%s:%d' % (dtmp['id'], width)
			dtmp['Kentropy'] = entropy(cs)
			assert 'Fentropy' in dtmp
			dtmp['width'] = width
			descr.append( dtmp )
	# pylab.show()
	return (o, descr)


def vowel_edge(width, ectrs, neural, neural_now, Nsv, do_abs=False,
			FORMANT_LOW=None, FORMANT_HIGH=None):
	VEfac = 0.7
	ce, cs = edgepair_win(width)
	nns = convolve(neural_now, cs)/Num.sum(cs)
	norm = Num.hypot(nns, Nsv * Num.sum(nns**2)/Num.sum(nns))
	# pylab.plot(norm)
	# pylab.figure()
	o = []
	descr = []
	for (i, e) in enumerate(ectrs):
		if e['type']=='band' and FORMANT_LOW < e['erb'] < FORMANT_HIGH:
			tmp = VEfac * convolve(neural[i], ce)/norm
			# pylab.plot(tmp)
			# print 'RMS', math.sqrt(Num.sum(tmp**2)/tmp.shape[0])
			dtmp = e.copy()
			dtmp['width'] = 2*width
			dtmp['Kentropy'] = entropy(cs)
			dtmp['Fentropy'] = 0.0
			if do_abs:
				o.append( Num.absolute(tmp) )
				dtmp['type'] = 'vowel |edge|'
				dtmp['id'] = 'vowel |edge|:%d:%.1f' % (width, e['erb'])
				descr.append( dtmp )
			else:
				o.append( tmp )
				dtmp['type'] = 'vowel edge'
				dtmp['id'] = 'vowel edge:%d:%.1f' % (width, e['erb'])
				descr.append( dtmp )
	# pylab.show()
	return (o, descr)


def fricative(width, ectrs, neural, neural_now, Nsv):
	CSSE = 0.7
	N = neural[0].shape[0]
	cs = win(width)
	css = Num.sum(cs)
	nns = convolve(neural_now, cs)/css
	norm = Num.hypot(nns, Nsv * Num.sum(nns**2)/Num.sum(nns))
	# pylab.plot(norm)
	# pylab.figure()
	o = []
	descr = []
	for (rs, re, fac) in [ (70.0, 600.0, 0.6), (600.0, 2000.0, 0.6),
				(2000.0, 3000.0, 0.6), (3000.0, 6000.0, 0.6) ]:
		tsum = Num.zeros((N,), Num.Float)
		elow = erb_scale.f_to_erb(rs)
		ehigh = erb_scale.f_to_erb(re)
		included = []
		nq = 0
		for (i, e) in enumerate(ectrs):
			if e['type']=='band' and elow < e['erb'] < ehigh:
				Num.add(tsum, neural[i], tsum)
				included.append(e)
				nq += 1
		tmp = (fac/css**CSSE) * convolve(tsum, cs)/(norm*nq)
		# print 'RMS', math.sqrt(Num.sum(tmp**2)/tmp.shape[0])
		# pylab.plot(tmp + len(o))
		o.append( tmp )
		descr.append( {'type': 'fricative', 'width': width,
				'erbs': [e['erb'] for e in included],
				'fcs' : [e['fc'] for e in included],
				'Kentropy': entropy(cs),
				'Fentropy': -math.log(len(included)),
				'id': 'fricative:%d:%.1f-%.1f' % (width, elow, ehigh)
				}
				)
	# pylab.show()
	return (o, descr)


def prominence(ectrs, neural, neural_now, Nsv):
	WIDTH = 20
	N = neural[0].shape[0]
	ce, cs = edgepair_win(WIDTH)
	css = Num.sum(cs)
	nns = convolve(neural_now, cs)
	norm = Num.hypot(nns, Nsv * Num.sum(nns**2)/Num.sum(nns))
	# pylab.plot(norm)
	# pylab.figure()
	o = []
	descr = []
	included = []
	for (rs, re, fac) in [ (70.0, 600.0, 0.22), (600.0, 2000.0, 0.25),
				(2000.0, 3000.0, 0.32), (3000.0, 6000.0, 0.35) ]:
		tsum = Num.zeros((N,), Num.Float)
		elow = erb_scale.f_to_erb(rs)
		ehigh = erb_scale.f_to_erb(re)
		for (i, e) in enumerate(ectrs):
			if e['type']=='band' and elow < e['erb'] < ehigh:
				Num.add(tsum, neural[i], tsum)
				included.append(e)
		tmp = (fac/css) * convolve(tsum, ce)/norm
		# pylab.plot(tmp + len(o))
		# print 'RMS', math.sqrt(Num.sum(tmp**2)/tmp.shape[0])
		o.append( tmp )
		dtmp = {'type': 'prominence', 'width': WIDTH,
				'erbs': [e['erb'] for e in included],
				'fcs' : [e['fc'] for e in included],
				'Kentropy': entropy(cs),
				'Fentropy': -math.log(len(included)),
				'id': 'prominence:%d:%.1f-%.1f' % (WIDTH, elow, ehigh)
				}
		descr.append( dtmp )
	# pylab.show()
	return (o, descr)




def fricative_edge(ectrs, neural, neural_now, Nsv, do_abs=False, width=2):
	CSSE = 1.6
	N = neural[0].shape[0]
	ce, cs = edgepair_win(width)
	css = Num.sum(cs)
	nns = convolve(neural_now, cs)/css
	norm = Num.hypot(nns, Nsv * Num.sum(nns**2)/Num.sum(nns))
	# pylab.plot(norm)
	# pylab.figure()
	o = []
	descr = []
	included = []
	for (rs, re, fac) in [(70.0, 800.0, 7), (800.0, 1500.0, 7),
				(1500.0, 2200.0, 7), (2200.0, 6000.0, 7)]:
		tsum = Num.zeros((N,), Num.Float)
		elow = erb_scale.f_to_erb(rs)
		ehigh = erb_scale.f_to_erb(re)
		nq = 0
		for (i, e) in enumerate(ectrs):
			if e['type']=='band' and elow < e['erb'] < ehigh:
				Num.add(tsum, neural[i], tsum)
				included.append(e)
				nq += 1
		tmp = (fac/css**CSSE) * convolve(tsum, ce)/(norm*nq)
		# pylab.plot(tmp)
		# print 'RMS', math.sqrt(Num.sum(tmp**2)/tmp.shape[0])

		dtmp = {'width': width, 
				'erbs': [e['erb'] for e in included],
				'fcs' : [e['fc'] for e in included],
				'Kentropy': entropy(cs),
				'Fentropy': -math.log(len(included))
				}

		if do_abs:
			o.append( Num.absolute(tmp) )
			dtmp['type'] = 'fricative |edge|'
		else:
			o.append( tmp )
			dtmp['type'] = 'fricative edge'
		dtmp['id'] = '%s:%d:%.1f-%.1f' % (dtmp['type'], width, elow, ehigh)
		descr.append( dtmp )
	# pylab.show()
	return (o, descr)


def burst(ectrs, neural, neural_now, Nsv):
	BKGWIDTH = 8
	WIDTH = 1
	N = neural[0].shape[0]
	ce,cs = burst_win(BKGWIDTH, 2)
	nns = convolve(neural_now, cs)/Num.sum(cs)
	norm = Num.hypot(nns, Nsv * Num.sum(nns**2)/Num.sum(nns))
	# pylab.plot(norm)
	# pylab.figure()
	o = []
	descr = []
	included = []
	# Burst bandwidth needs to be large enough so that the
	# burst can fit into a 10ms slot.
	for (rs, re, fac) in [ (150.0, 500.0, 1.0), (500.0, 1200.0, 1.0),
				(1200.0, 2800.0, 1.0), (2800.0, 6000.0, 1.0) ]:
		tsum = Num.zeros((N,), Num.Float)
		elow = erb_scale.f_to_erb(rs)
		ehigh = erb_scale.f_to_erb(re)
		for (i, e) in enumerate(ectrs):
			if e['type']=='band' and elow < e['erb'] < ehigh:
				Num.add(tsum, neural[i], tsum)
				included.append( e )
		tss = fac * convolve(tsum, ce)/norm
		# pylab.plot(tmp + len(o))
		# print 'RMS', math.sqrt(Num.sum(tmp**2)/tmp.shape[0])
		o.append( tss )
		descr.append( {'type': 'burst', 'width': WIDTH,
				'bkgwidth': BKGWIDTH,
				'erbs': [e['erb'] for e in included],
				'fcs' : [e['fc'] for e in included],
				'Kentropy': entropy(cs),
				'Fentropy': -math.log(len(included)),
				'id': 'burst:%d:%.1f-%.1f'
					% (WIDTH, elow, ehigh)
				}
				)
	# pylab.show()
	return (o, descr)



import gpkavg

def average(x):
	vv = []
	ww = []
	for (v,wt) in x:
		vv.append(v)
		ww.append(wt)
	return gpkavg.avg(vv, ww, 0.0)[0]

def median(x):
	vv = []
	ww = []
	for (v,wt) in x:
		vv.append(v)
		ww.append(wt)
	return gpkavg.avg(vv, ww, 0.499)[0]


def weight(x):
	sum = 0.0
	for (v,wt) in x:
		sum += wt**2
	return math.sqrt(sum)



def describe_xform(descr, fac):
	nin, nout = fac.shape
	assert len(descr) == nin
	for i in range(nout):
		norm = math.sqrt(Num.average(fac[:,i]**2))
		nf = fac[:,i]/norm
		tmp = []
		fwt = []
		wwt = []
		edginess = []
		voiciness = []
		burstiness = []
		friciness = []
		vness = []
		for j in range(nin):
			dj = descr[j]
			if dj.has_key('erb'):
				fwt.append( (dj['erb'], abs(nf[j])) )
			if dj.has_key('width'):
				wwt.append( (dj['width'], abs(nf[j])) )
			if 'edge' in dj['type']:
				edginess.append( abs(nf[j]) )
			if 'burst' in dj['type']:
				burstiness.append( abs(nf[j]) )
			if 'fricative' in dj['type']:
				friciness.append( abs(nf[j]) )
			if 'vowel' in dj['type']:
				vness.append( abs(nf[j]) )
			if 'haspitch' in dj['type']:
				voiciness.append( abs(nf[j]) )
			if abs(nf[j]) > 0.1:
				tmp.append('%+.2f*%s' % (nf[j], dj['id']) )
		print '# FV[%d]= %s' % (i, ' '.join(tmp))
		fb = {'voicing': math.sqrt(Num.sum(Num.array(voiciness)**2)),
			'edges': math.sqrt(Num.sum(Num.array(edginess)**2)),
			'burst': math.sqrt(Num.sum(Num.array(burstiness)**2)),
			'fricative': math.sqrt(Num.sum(Num.array(friciness)**2)),
			'vowel': math.sqrt(Num.sum(Num.array(vness)**2)),
			'meanfreq': average(fwt), 'medfreq': median(fwt),
			'wt_freq': weight(fwt),
			'meanwidth': average(wwt), 'medwidth': median(wwt),
			'wt_width': weight(wwt),
			'channel': i, 'description': ' '.join(tmp),
			'ltype': 'fb'
			}
		print avio.concoct(fb)



__version__ = "$Revision: 1.65 $"
__date__ = "$Date: 2007/04/05 15:34:43 $"

XFORM = None

if __name__ == '__main__':
	import gpkimgclass
	try:
		import psyco
		psyco.full()
	except ImportError:
		pass
	ofile = '-'
	arglist = sys.argv[1:]
	verbose = 0
	column = 0
	DoVoicing = True
	DoDissonance = True
	fvf = feature_vec
	while arglist and arglist[0].startswith('-'):
		arg = arglist.pop(0)
		if arg == '--':
			break
		elif arg == '-o':
			ofile = arglist.pop(0)
		elif arg == '-v':
			verbose += 1
		elif arg == '-Nsv':
			NSV = float(arglist.pop(0))
		# elif arg == '-SpecExp':
			# SpecExp = float(arglist.pop(0))
		elif arg == '-col':
			column = arglist.pop(0)
		elif arg == '-DT':
			Dt = float(arglist.pop(0))
		elif arg == '-sfv':
			fvf = simple_feature_vec
		elif arg == '-ssfv':
			fvf = ss_feature_vec
			DoDissonance = False
		elif arg == '-fv20071030':
			fvf = feature_vec20071030
		elif arg == '-DB':
			DB = float(arglist.pop(0))
		elif arg == '-LF':
			LF = float(arglist.pop(0))
		elif arg == '-ELF':
			Elf = float(arglist.pop(0))
		elif arg == '-novoicing':
			DoVoicing = False
		elif arg == '-xform':
			fxd = os.environ['OXIVOICE']
			XFORM = '%s/xform.chunk' % fxd
		elif arg == '-Xform':
			XFORM = arglist.pop(0)
		else:
			die.die('Unrecognized flag: %s' % arg)
	fname = arglist[0]
	data = gpkimgclass.read(fname)
	o, descr, DTx, t0 = fvf(data.column(column), data.dt(),
					Nsv=NSV,
					# SpecExp=SpecExp,
					LF=Lf, DT=Dt, ELF=Elf,
					do_voicing=DoVoicing,
					do_dissonance=DoDissonance
					)
	o = Num.transpose(o)
	hdr = {'CDELT2': DTx, 'CRPIX2': 1, 'CRVAL2': data.start()+t0,
		'VERSION': __version__,
		'BITPIX': -32, 'Nsv': NSV,
		'FNAME': fname,
		# 'SpecExp': SpecExp,
		'DataSamplingFreq': 1.0/data.dt(),
		'LF': Lf, 'Nsv': NSV, 'ELF': Elf
		}
	if XFORM is not None:
		import chunkio
		fac = chunkio.datachunk(open(XFORM, 'r')).read_NumArray()
		o = Num.matrixmultiply(o, fac)
		if verbose:
			describe_xform(descr, fac)
		descr = [ {'id': 'Mixture%d'% i} for i in range(o.shape[1]) ]
		hdr['XFORM'] = XFORM
			
	if PLOT:
		pylab.matshow(Num.transpose(o))
		pylab.show()
	assert o.shape[1] == len(descr), "Length mismatch data=%s descr=%d" % (
						o.shape, len(descr)
						)
	for (i,d) in enumerate(descr):
		hdr['TTYPE%d' % (i+1)] = d['id']
		hdr['F_INFO%d' % (i+1)] = avio.concoct(d)
		hdr['RMS%d' % (i+1)] = math.sqrt(Num.average(o[:,i]**2)) 
	gpkimgclass.gpk_img(hdr, o).write(ofile)


