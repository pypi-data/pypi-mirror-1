#!/usr/bin/env python

import Num
import math
import hilbert_xform


def smooth(ph, dt_in, dt_out, extra=0.0, wt=None):
	"""Smooths a data set, simultaneously resampling to
	a lower sampling rate.   It uses successive boxcar averages
	followed by decimations for the initial smooth, then a convolution
	with a Gaussian.   Even if C{dt_out>>dt_in}, it only uses
	C{O[log(dt_out/dt_in)} operations.
	@param dt_in: input sampling rate.
	@param dt_out: output sampling rate.
	@param extra: extra smoothing time constant to apply.
		Extra is the standard deviation of a Gaussian kernel smooth that is
		applied as the last step.
		This last step is not implemented efficiently, so if if C{extra>>dt_out}
		it can slow down the algorithm substantially.
	@type extra: float  (in the same units as dt_in and dt_out).
	@type dt_in: float  (in the same units as extra and dt_out).
	@type dt_out: float  (in the same units as dt_in and extra).
	@param ph: a 1???-dimensionan array containing data to be smoothed.
		(Query: will this work for higher-dimensional data?)
	@type ph: L{numpy.array}.
	@return: C{(rv, t0)} where C{rv} is a L{numpy} array and C{t0} it a C{float}
		offset of the first element, relative to the start of the input data.
	"""
	assert dt_in <= dt_out
	dt_ratio = dt_in/dt_out
	no = int(math.floor(ph.shape[0]*dt_ratio))
	# print 'no=', dt_in, len(ph), dt_out, dt_in*len(ph)/dt_out
	dti = dt_in
	# In vari, we accumulate the width of the equivalent
	# convolution kernel that has been applied so far.
	# Specifically, it is the second moment of the kernel.
	if wt is not None:
		ph = ph * wt
		weight = wt
	else:
		weight = 1
	kwi = 0.0
	t0 = 0.0
	while dti < 0.33*dt_out:
		# print "ph=", ph
		n = ph.shape[0] - ph.shape[0]%2
		ph = ph[0:n-1:2] + ph[1:n:2]
		if wt is not None:
			weight = weight[0:n-1:2] + weight[1:n:2]
		else:
			weight *= 2
		t0 += 0.5*dti
		kwi += (dti/2.0)**2
		dti *= 2.0
	# kwo is the desired width of the convolution kernel
	# between th input and output data streams.
	# It is just the second moment of a rectangular boxcar average.
	kwo = extra**2 + dt_out**2/12.0 - dt_in**2/12.0
	# kwx is the extra smoothing kernel that is yet to be applied.
	kwx = kwo - kwi
	assert kwx >= 0.0

	# print 'ph=', ph
	# Now, we set up a Gaussian of the appropriate width
	# to do the final convolution.
	if kwx > 0.0:
		N = int(math.ceil(2.3*math.sqrt(kwx)/dti))
		i = Num.arrayrange(2*N+1) - N
		k0 = Num.exp( (-1/(2*kwx)) * (i*dti)**2 )
		assert k0.shape[0] < ph.shape[0]
		kernel = k0/Num.sum(k0)
		ph = Num.convolve(ph, kernel, 1)
		if wt is not None:
			weight = Num.convolve(weight, kernel, 1)
	Num.divide(ph, weight, ph)
	# print 'phs=', ph

	# Then grab the necessary samples.
	q = Num.arange(no)*(dt_out/dti)
	qi = Num.around(q).astype(Num.Int)
	assert qi[-1] < ph.shape[0]
	rv = Num.take(ph, qi)
	assert rv.shape[0] == no
	return (rv, t0)


def local_power(d, dt_in, dt_out, extra=0.0):
	""" THIS IS WRONG!   IT PROBABLY SHOULD BE something like
	sqrt(d**2 + hilbert_transform(d)**2).
	The hilbert transform just supplies the imaginary part of
	an analytic function.   Current code leaves out the
	read part!
	"""
	raise RuntimeError, "Bug!"
	cutoff = math.hypot(dt_out, extra)/dt_in
	ph = Num.absolute(hilbert_xform.hilbert(d, cutoff))
	return smooth(ph, dt_in, dt_out, extra)


def test1():
	x = Num.zeros((50,), Num.Float)
	x[10:] = 1.0
	k = [0.1, 0.2, 0.4, 0.2, 0.1]
	xk = Num.convolve(x, k, 1)
	xs0, ts0 = smooth(x, 1.0, 1.0, 0.01)
	xs1, ts1 = smooth(x, 1.0, 1.0, 1.0)
	xs2, ts2 = smooth(x, 1.0, 1.0, 2.0)
	for i in range(20):
		print i, x[i], xk[i], xs0[i], xs1[i], xs2[i]
		assert Num.alltrue( Num.equal(Num.less(x, 0.5),
						Num.less(xk, 0.5)
						)
					)
		assert Num.alltrue( Num.equal(Num.less(x, 0.5),
						Num.less(xs0, 0.5)
						)
					)
		assert Num.alltrue( Num.equal(Num.less(x, 0.5),
						Num.less(xs1, 0.5)
						)
					)
		assert Num.alltrue( Num.equal(Num.less(x, 0.5),
						Num.less(xs2, 0.5)
						)
					)


def test2():
	x = Num.zeros((500,), Num.Float)
	x[100:] = 1.0
	xs0, ts0 = smooth(x, 0.1, 1.0, 0.01)
	xs1, ts1 = smooth(x, 0.1, 1.0, 1.0)
	xs2, ts2 = smooth(x, 0.1, 1.0, 2.0)
	for i in range(200):
		if i%10 == 5:
			print i, x[i], xs0[i/10], xs1[i/10], xs2[i/10]
		else:
			print i, x[i]

def test3():
	x = Num.zeros((200,), Num.Float)
	x[100] = 1.0
	xs0, ts0 = smooth(x, 0.1, 0.1, 0)
	xs1, ts1 = smooth(x, 0.1, 0.3, 0)
	xs2, ts2 = smooth(x, 0.1, 0.9, 0)
	xs3, ts3 = smooth(x, 0.1, 1.5, 0)
	for i in range(197):
		o = [ '%d'%i ]
		o.append( '%g' % x[i])
		o.append( '%g' % xs0[i])
		if i%3 == 1:
			o.append('%g' % xs1[i//3])
		else:
			o.append('')

		if i%9 == 5:
			o.append('%g' % xs2[i//9])
		else:
			o.append('')

		if i%15 == 7:
			o.append('%g' % xs3[i//15])
		else:
			o.append('')

		print '\t'.join(o)


if __name__ == '__main__':
	test1()
	test2()
	test3()
