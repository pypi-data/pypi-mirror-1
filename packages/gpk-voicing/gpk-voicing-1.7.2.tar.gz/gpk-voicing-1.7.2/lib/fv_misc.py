
import re
import math

from gmisclib import die
from gmisclib import Num
from gmisclib import gpkmisc
from gmisclib import g_encode
from gmisclib import erb_scale
from gmisclib import Numeric_gpk as NG
from gpk_voicing import voice_misc
try:
	from gpk_voicing import pseudo_dur as PD
except ImportError:
	PD = None

pylab = None
# import pylab

DB = math.sqrt(0.5)
NSV = 0.75
# Dt = 0.005
C = 10.0


class SillyWidthException(ValueError):
	def __init__(self, *s):
		ValueError.__init__(self, *s)


# def edgepair_win(n):
	# e = Num.zeros((2*n,), Num.Float)
	# e[:n] = -1.0
	# e[n:] = 1.0
	# s = Num.ones((2*n), Num.Float)
	# return (e, s)


def edgepair_win(n):
	if not n > 0:
		raise SillyWidthException, n
	tmp0 = voice_misc.window(2*n, 0)
	tmp1 = voice_misc.window(2*n, 1)
	norm = gpkmisc.N_maximum(tmp0)
	return (tmp1/norm, tmp0/norm)


# def win(n):
	# tmp = Num.ones((n,), Num.Float)
	# return tmp

def win(n):
	if not n > 0:
		raise SillyWidthException, n
	tmp = voice_misc.window(n, 0)
	return tmp/gpkmisc.N_maximum(tmp)


def burst_win(n, i):
	if not n > 0:
		raise SillyWidthException, n
	tmp = Num.zeros((n,), Num.Float)
	tmp[i] = 1.0
	neg = win(n)
	nneg = neg/Num.sum(neg)
	return (tmp - nneg, nneg)


def entropy(w):
	assert Num.alltrue( Num.greater(w, 0.0) )
	p = w/Num.sum(w)
	return -Num.sum(p*Num.log(p))

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
			dtmp['t_symmetry'] = 1
			dtmp['a_scaling'] = 1
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
	SEF = 1.0
	EPS = 1e-6
	cs = win(width)
	assert Num.alltrue( Num.greater(cs, 0.0) )

	nnt = []
	nns = Num.zeros(neural.shape[1], Num.Float)
	for (i, e) in enumerate(ectrs):
		if e['type']=='band':
			assert Num.alltrue( Num.greater_equal(neural[i], 0.0) )
			tmp = convolve(neural[i], cs)
			nnt.append(tmp)
			Num.add(nns, tmp, nns)

	np = len(nnt)
	ent_sum = Num.zeros(neural.shape[1], Num.Float) + math.log(4.0)
	for tmp in nnt:
		Num.divide(tmp, nns, tmp)
		Num.add(tmp, EPS*nns, tmp)
		etmp = tmp*Num.log(tmp)
		Num.add(ent_sum, etmp, ent_sum)
	Num.multiply(ent_sum, -SEF, ent_sum)
	# pylab.title('spectral_entropy')
	# pylab.show()
	assert np > 0
	dtmp = {'type': 'spectral_entropy',
		'width': width,
		'Kentropy': entropy(cs),
		'Fentropy': math.log(np),
		'id': 'Sentropy:%d' % width,
		't_symmetry': 1,
		'a_scaling': 0
		}
	return ([ent_sum], [dtmp])


def space_time_entropy(width, ectrs, neural, neural_now, Nsv):
	assert Nsv > 0.0
	SEF = 1.0
	EPS = 1e-6
	cs = win(width)

	nnt = []
	nns = Num.zeros(neural.shape[1], Num.Float)
	for (i, e) in enumerate(ectrs):
		if e['type']=='band':
			assert Num.alltrue( Num.greater_equal(neural[i], 0.0) )
			nnt.append(neural[i])
			Num.add(nns, neural[i], nns)

	np = len(nnt)
	nns = convolve(nns, cs)
	ent_sum = Num.zeros(neural.shape[1], Num.Float) + math.log(3.0*np)
	for tmp in nnt:
		Num.divide(tmp, nns, tmp)
		Num.add(tmp, EPS*nns, tmp)
		etmp = convolve(tmp*Num.log(tmp), cs)
		Num.add(ent_sum, etmp, ent_sum)
	Num.multiply(ent_sum, -SEF, ent_sum)
	# pylab.title('spectral_entropy')
	# pylab.show()
	assert np > 0
	dtmp = {'type': 'space_time_entropy',
		'width': width,
		'Kentropy': entropy(cs),
		'Fentropy': math.log(np),
		'id': 'STentropy:%d' % width,
		't_symmetry': 1,
		'a_scaling': 0
		}
	return ([ent_sum], [dtmp])



def haspitch(width, ectrs, neural, neural_now, Nsv):
	HFAC = {'high': 20.0, 'all': 10.0, 1: 10.0}
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
			dtmp['t_symmetry'] = 1
			dtmp['a_scaling'] = 1
			descr.append( dtmp )
	# pylab.show()
	return (o, descr)



def peakiness(width, ectrs, neural, neural_now, Nsv):
	HFAC = 10
	cs = win(width)
	css = Num.sum(cs)
	nns = convolve(neural_now, cs)/Num.sum(cs)
	norm = Num.hypot(nns, Nsv * Num.sum(nns**2)/Num.sum(nns))
	o = []
	descr = []
	for (i, e) in enumerate(ectrs):
		if e['type'].startswith('peakalign'):
			tmp = (HFAC/css)*convolve(neural[i], cs)/norm
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
			dtmp['t_symmetry'] = 1
			dtmp['a_scaling'] = 1
			descr.append( dtmp )
	# pylab.show()
	return (o, descr)


def pdur(ectrs, neural, neural_now, Dt, Cfac=1.0):
	if PD is None:	# If pseuduration is not available.
		return ([], [])
	TYPICAL = 0.100
	c = C * Cfac
	norm = Num.sum(neural_now**2)/Num.sum(neural_now)
	no = neural_now.shape[0]
	out = Num.zeros((no,), Num.Float)
	for t in range(no):
		plm, pcm = PD.pdur_guts(neural.transpose(), t, -1, Dt, c/norm**2)
		plp, pcp = PD.pdur_guts(neural.transpose(), t, 1, Dt, c/norm**2)
		out[t] = plm + plp
	if pylab:
		pylab.figure()
		pylab.title('pdur')
		pylab.plot(out)
		pylab.show()
	nbands = 0
	for e in ectrs:
		if e['type']=='band':
			nbands += 1
	assert nbands > 0
	typical = NG.N_median(out)
	descr = [ {'id': 'pseudoduration:%f' % c,
		'Kentropy': NG.N_median(Num.log(out)),
		'Fentropy': math.log(nbands),
		'width': typical,
		't_symmetry': 1, 'a_scaling': 0
		} ]
	return ([Num.log(out/TYPICAL)], descr)


def roughness(width, ectrs, neural, neural_now, Nsv):
	HFAC = {1: 4.0}
	cs = win(width)
	css = Num.sum(cs)
	nns = convolve(neural_now, cs)/Num.sum(cs)
	norm = Num.hypot(nns, Nsv * Num.sum(nns**2)/Num.sum(nns))
	o = []
	descr = []
	for (i, e) in enumerate(ectrs):
		if e['type'].startswith('roughness'):
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
			dtmp['t_symmetry'] = 1
			dtmp['a_scaling'] = 1
			descr.append( dtmp )
	# pylab.show()
	return (o, descr)

dissonance = roughness	# obsolete


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
			dtmp['t_symmetry'] = -1
			dtmp['a_scaling'] = 1
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
	for (rs, re, fac) in [(70.0, 700.0, 0.6), (700.0, 1500.0, 0.6),
				(1500.0, 2500.0, 0.9), (2500.0, 4000.0, 1.1),
				(4000.0, 6000.0, 1.3)
				]:
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
				'id': 'fricative:%d:%.1f-%.1f' % (width, elow, ehigh),
				't_symmetry': 1, 'a_scaling': 1
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
				'id': 'prominence:%d:%.1f-%.1f' % (WIDTH, elow, ehigh),
				't_symmetry': 1, 'a_scaling': 1
				}
		descr.append( dtmp )
	# pylab.show()
	return (o, descr)




def fricative_edge(width, ectrs, neural, neural_now, Nsv, do_abs=False):
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
	for (rs, re, fac) in [(70.0, 700.0, 7), (700.0, 1500.0, 7),
				(1500.0, 2500.0, 7), (2500.0, 4000.0, 7),
				(4000.0, 6000.0, 7)
				]:
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
		tmp = (fac/css**CSSE) * convolve(tsum, ce)/(norm*nq)
		# pylab.plot(tmp)
		# print 'RMS', math.sqrt(Num.sum(tmp**2)/tmp.shape[0])

		dtmp = {'width': width, 
				'erbs': [e['erb'] for e in included],
				'fcs' : [e['fc'] for e in included],
				'Kentropy': entropy(cs),
				'Fentropy': -math.log(len(included)),
				'a_scaling': 1
				}

		if do_abs:
			o.append( Num.absolute(tmp) )
			dtmp['type'] = 'fricative |edge|'
			dtmp['t_symmetry'] = 1
		else:
			o.append( tmp )
			dtmp['type'] = 'fricative edge'
			dtmp['t_symmetry'] = -1
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
					% (WIDTH, elow, ehigh),
				't_symmetry': 1, 'a_scaling': 1
				}
				)
	# pylab.show()
	return (o, descr)



class scale_xform(object):
	def __init__(self, opt_string, name='???', prefix='scale'):
		self.prefix = prefix
		self._name = name
		self.sc = []
		for tmp in opt_string.split('\n'):
			if tmp=='' or tmp.startswith('#'):
				continue
			v, k = tmp.split()
			self.sc.append( (re.compile(k), float(v)) )
		self._e = g_encode.encoder(notallowed=' %,')

	def get(self, k):
		for (pat,v) in self.sc:
			if pat.match(k):
				return v
		raise KeyError, "scale_xform.get(%s): no matching pattern." % k

	def get_many(self, *k):
		for q in k:
			yield self.get(q)

	def name(self):
		return self._name

	def operate(self, o, descr):
		assert o.shape[1] == len(descr)
		for (i,d) in enumerate(descr):
			k = '%s,%s' % (self.prefix, self._e.fwd(d['id']))
			scalefac = math.exp(self.get(k))
			Num.multiply(o[:,i], scalefac, o[:,i])
			d['id'] = d['id'] + '(scaled)'
			d['scalefac'] = scalefac

	def describe_xform(self):
		pass
