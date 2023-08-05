import djt_spectrum
import math
import Num
import voice_misc



def cep(d, n, K, step, w=None, exfac1=1, exfac2=1):
	assert len(d.shape)==1
	if w==None:
		w = 0.5*float(K+2)/float(n)
	ns = int(math.floor((d.shape[0]-n)/step))
	o = []
	for i in range(ns):
		print "dl=", d[i*step:(i+1)*step].shape, "w=", w, "k=", K, "ex1=", exfac1
		q = djt_spectrum.transform(d[i*step:i*step+n], w, K, exfac1)
		c = djt_spectrum.q_cepstrum(q, exfac2)
		o.append(c)
	return Num.array(o, copy=True)


def spec(d, K, w=None, exfac=1, wts=None):
	assert len(d.shape)==1
	n = len(d)
	if w==None:
		w = 0.5*float(K)/float(n)
	print "w=", w, "K=", K, "n=", n
	q = djt_spectrum.transform(d, w, K, exfac)
	c = djt_spectrum.S(q, wts)
	return c

def logspec(d, K, w=None, exfac=1, wts=None):
	return Num.log(spec(d, K, w, exfac, wts))


def stepped_spec(d, n, K, step, w=None, exfac=1, wts=None):
	ns = int(math.floor((d.shape[0]-n)/step))
	o = []
	for i in range(ns):
		c = spec(d[i*step:i*step+n], K, w, exfac, wts)
		o.append(c)
	return Num.array(o, copy=True)



# print factor(1)
# print factor(2)
# print factor(3)
# print factor(4)
# print factor(5)
# print factor(6)
# print factor(7)
# print factor(8)
# print factor(9)
# print factor(10)
# print factor(11)
# print factor(12)


if __name__ == '__main__':
	import gpkimgclass
	K = 4
	tmax = 1.0/40.0	# seconds
	tau_step = 0.010	# seconds.
	tau = 2 * tmax
	if 1:
		a = gpkimgclass.read('foo.d')
		dt = a.dt();
		data = a.d[:,0]
		hdr = a.hdr.copy()
	else:
		hdr = {'CRPIX2':0}
		dt = 1.0/8000.0
		t = Num.arrayrange(4096)*(2*math.pi/50.0)
		data = (Num.exp(5*Num.cos(t))-Num.exp(4*Num.cos(t-0.8)))*Num.cos(t/20)+Num.cos(t*t*13.0)+Num.sin(100.0*Num.sqrt(t))
	od = gpkimgclass.gpk_img(hdr, Num.transpose(Num.array((data,))))
	od.write('tmp.fits')
	nw = voice_misc.near_win_size(tau/dt, 5)
	step = int(round(tau_step/dt))
	print "step=", step, "nw=", nw, "dt=", dt
	os = stepped_spec(data, nw, K, step, w=None, exfac=2)
	oc = cep(data, nw, K, step, w=None, exfac1=2, exfac2=2)
	hdr['CDELT2'] = nw * dt
	hdr['CRPIX2'] = float(hdr['CRPIX2'])/step
	hdr['CRVAL1'] = 0
	hdr['CRPIX1'] = 0
	# hdr['CDELT1'] = dt/2
	hdr['CDELT1'] = math.pi/dt
	oos = gpkimgclass.gpk_img(hdr, os)
	oos.write('bar.fits')
	ooc = gpkimgclass.gpk_img(hdr, oc)
	ooc.write('gleep.fits')
