"""This works with feature_vec.py.   Incomplete."""

def plot_xform(descr, fac):
	DW = 0.5
	WMAX = 60
	DF = 0.5
	FMAX = 80
	WH = WMAX//2
	import pylab
	nin, nout = fac.shape
	assert len(descr) == nin
	for i in range(nout):
		print 'i=', i
		pylab.figure(i)
		tmp = Num.zeros((WMAX,FMAX), Num.Float)
		norm = math.sqrt(Num.average(fac[:,i]**2))
		nf = fac[:,i]/norm
		for j in range(nin):
			dj = descr[j]
			if '|edge|' in dj['type'] or 'haspitch' in dj['type']:
				continue
			if 'burst' in dj['type']:
				k = lambda delta: [1.0,-.125][abs(delta)<=1]
			elif ' edge' in dj['type']:
				k = lambda delta: [1.0, -1.0][delta<0]
			else:
				k = lambda delta: 1.0

			if dj.has_key('erb') and dj.has_key('width'):
				erbs = [dj['erb']]
			elif dj.has_key('erbs') and dj.has_key('width'):
				erbs = dj['erbs']
			else:
				continue
			nfj = nf[j]/dj['width']
			w0 = WH - int(round(dj['width']/(DW*2.0)))
			we = WH + int(round(dj['width']/(DW*2.0)))
			assert w0>=0 and we<WMAX
			for e in erbs:
				ifreq = int(round(e/DF))
				assert ifreq > 0
				print 'w0:we=', w0, we, 'ifreq=', ifreq, 'tmp.shape', tmp.shape, 'nfj=', nfj
				for w in range(w0, we+1):
					tmp[w,ifreq] += k(w-WH)*nfj
					tmp[w,ifreq-1] += k(w-WH)*nfj/2.0
					tmp[w,ifreq+1] += k(w-WH)*nfj/2.0
		maxabs = gpkmisc.N_maximum(Num.absolute(Num.ravel(tmp)))
		pylab.imshow(Num.transpose(tmp), vmin=-maxabs, vmax=maxabs)
		print
