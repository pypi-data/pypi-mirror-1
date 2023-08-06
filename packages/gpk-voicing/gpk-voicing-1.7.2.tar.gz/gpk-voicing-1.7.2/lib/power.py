#!/usr/bin/env python

import math
import numpy
from gmisclib import hilbert_xform
from gpk_voicing import power1 as P1

# import pylab

def calc_var_of_window():
	N = 100
	phase = (math.pi/float(N))*(numpy.arange(N)+0.5)
	w = 1 + numpy.cos(phase)
	return numpy.sum(w*phase**2)/numpy.sum(w)

_ALPHA = 1.0/math.sqrt(calc_var_of_window())


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
	@param ph: Normally a 1-dimensional array containing data to be smoothed.
		If the data is higher-dimensional, the time axis is assumed to run
		along axis=0, and the return value will be an array of the same dimension.
	@type ph: L{numpy.ndarray}.
	@param ph: None (which indicates a uniform weighting) or
		a L{numpy.ndarray} that is the same length (axis 0) as C{ph}.
	@type wt: L{numpy.ndarray}
	@return: C{(rv, t0)} where C{rv} is a L{numpy} array and C{t0} it a C{float}
		offset of the first element, relative to the start of the input data.
	"""
	assert dt_in <= dt_out
	dt_in = float(dt_in)
	dt_ratio = float(dt_out)/dt_in
	w = math.hypot(dt_out, _ALPHA*extra)
	# print "w=", w, "dt_ratio=", dt_ratio, "ALPHA=", _ALPHA, "extra=", extra, "dt_in=", dt_in
	assert w >= dt_in

	# First, we try to see if it makes sense to do it in three
	# passes:
	dt_m1 = min(dt_out, ((w/dt_in)**0.667)*dt_in)
	ifac = int(round(dt_out/dt_m1))
	dt_m1 = dt_out/ifac
	assert dt_in <= dt_m1 <= dt_out
	dt_m2 = dt_m1/int(round(math.sqrt(dt_m1/dt_in)))
	assert dt_in <= dt_m2 <= dt_m1
	if w >= 3*dt_m1 and dt_m1 >= 3*dt_m2 and dt_m2 >= 3*dt_in:
		# print '3 steps:', dt_in, dt_m2, dt_m1, dt_out
		# pylab.plot(numpy.arange(ph.shape[0])*dt_in, ph)
		# print "dt_m1/dt_m2=", dt_m2/dt_in
		sm2, wt2 = P1.smooth_guts(ph, dt_in, dt_m2, dt_m2/dt_in, wt)
		# pylab.plot(numpy.arange(sm2.shape[0])*dt_m2, sm2)
		# print "dt_m1/dt_m2=", dt_m1/dt_m2
		sm1, wt1 = P1.smooth_guts(sm2, dt_m2, dt_m1, dt_m1/dt_m2, wt2)
		# pylab.plot(numpy.arange(sm1.shape[0])*dt_m1, sm1)
		# print "dt_m1=", dt_m1, "dt_out=", dt_out, "w/dt_m1=", w/dt_m1
		tmp = P1.smooth_guts(sm1, dt_m1, dt_out, w/dt_m1, wt1)[0]
		# pylab.plot(numpy.arange(tmp.shape[0])*dt_out, tmp)
		return (tmp, 0.0)
		# return (P1.smooth_guts(sm1, dt_m1, dt_out, w/dt_m1, wt1)[0], 0.0)
	# If not, we try to see if it makes sense to do it in two
	# passes:
	dt_mid = min(dt_out, math.sqrt(w*dt_in))
	ifac = int(round(dt_out/dt_mid))
	dt_mid = dt_out/ifac
	assert dt_in <= dt_mid <= dt_out
	if w >= 3*dt_mid and dt_mid >= 3*dt_in:
		# print '2 steps'
		sm1, wt1 = P1.smooth_guts(ph, dt_in, dt_mid, dt_mid/dt_in, wt)
		return (P1.smooth_guts(sm1, dt_mid, dt_out, w/dt_mid, wt1)[0], 0.0)
	# Otherwise, we do it in a single pass.
	# print '1 step'
	return (P1.smooth_guts(ph, dt_in, dt_out, w/dt_in, wt)[0], 0.0)


def smooth_guts(ph, dt_in, dt_out, w, wt=None):
	assert w >= 1.0
	assert dt_in <= dt_out
	dt_ratio = dt_out/dt_in
	no = int(math.floor(ph.shape[0]/dt_ratio))
	o = numpy.zeros((no,)+ph.shape[1:], numpy.float)
	if wt is not None:
		owt = numpy.zeros((no,)+ph.shape[1:], numpy.float)

	# print 'w=', w, 'dj=', dj, 'dt_ratio=', dt_ratio
	tmp0 = numpy.zeros((int(2*w)+3,))
	cache = {}
	SS = float(10.0)
	ni = ph.shape[0]
	for i in range(no):
		jr = i*dt_ratio
		jrr = round(jr*SS)/SS
		j0 = max(0, int(math.ceil(jrr-w)))
		je = min(ni, int(math.floor(jrr+w))+1)
		wkey = (je-j0, jrr-j0)
		try:
			window, wsum = cache[wkey]
		except KeyError:
			window = _wfunc(je-j0, jrr-j0, w)
			wsum = numpy.sum(window)
			cache[wkey] = (window, wsum)
		tmp = tmp0[:je-j0]
		if wt is not None:
			numpy.multiply(wt[j0:je], window, tmp)
			# owt[i] = numpy.sum(wt[j0:je]*window, axis=0)
			owt[i] = numpy.sum(tmp)
			numpy.multiply(tmp, ph[j0:je], tmp)
			# o[i] = numpy.sum(ph[j0:je]*wt[j0:je]*window, axis=0)/owt[i]
			o[i] = numpy.sum(tmp)/owt[i]
		else:
			numpy.multiply(ph[j0:je], window, tmp)
			# o[i] = numpy.sum(ph[j0:je]*window, axis=0)/numpy.sum(window, axis=0)
			o[i] = numpy.sum(tmp)/wsum
			owt = None
	return o, owt


def _wfunc(n, ctr, w):
	phase = (math.pi/w) * (numpy.arange(n) - ctr)
	# print 'phases for', n, ctr, w, '=', phase
	assert phase[0]>=-3.142 and phase[-1]<=3.142, "Bad phases: %s or %s for %s %s %s" % (str(phase[0]), str(phase[-1]), str(n), str(ctr), str(w))
	return 1.0 + numpy.cos(phase)


def old_smooth(ph, dt_in, dt_out, extra=0.0, wt=None):
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
	dt_ratio = dt_out/dt_in
	no = int(math.floor(ph.shape[0]/dt_ratio))
	# print 'no=', dt_in, len(ph), dt_out, dt_in*len(ph)/dt_out
	dti = dt_in
	# In vari, we accumulate the width of the equivalent
	# convolution kernel that has been applied so far.
	# Specifically, it is the second moment of the kernel.
	if wt is not None:
		ph = ph * wt
		weight = wt
	else:
		weight = numpy.ones((ph.shape[0],), numpy.int32)
	kwi = 0.0
	t0 = 0.0
	while dti < 0.33*dt_out:
		# print "ph=", ph
		nph = numpy.array(ph[::2], copy=True)
		ph12 = ph[1::2]
		numpy.add(nph[:ph12.shape[0]], ph12, nph[:ph12.shape[0]])
		del ph12
		ph = nph
		nwt = numpy.array(weight[::2], copy=True)
		wt12 = weight[1::2]
		numpy.add(nwt[:wt12.shape[0]], wt12, nwt[:wt12.shape[0]])
		del wt12
		weight = nwt

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
		i = numpy.arange(2*N+1) - N
		k0 = numpy.exp( (-1/(2*kwx)) * (i*dti)**2 )
		assert k0.shape[0] < ph.shape[0]
		kernel = k0/numpy.sum(k0)
		ph = numpy.convolve(ph, kernel, 1)
		if wt is not None:
			weight = numpy.convolve(weight, kernel, 1)
	numpy.divide(ph, weight, ph)
	# print 'phs=', ph

	# Then grab the necessary samples.
	q = numpy.arange(no)*(dt_out/dti)
	qi = numpy.around(q).astype(numpy.int)
	assert qi[-1] < ph.shape[0]
	rv = numpy.take(ph, qi)
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
	ph = numpy.absolute(hilbert_xform.hilbert(d, cutoff))
	return smooth(ph, dt_in, dt_out, extra)


def test1():
	x = numpy.zeros((50,), numpy.float)
	x[10:] = 1.0
	k = [0.1, 0.2, 0.4, 0.2, 0.1]
	xk = numpy.convolve(x, k, 1)
	xs0, ts0 = smooth(x, 1.0, 1.0, 0.01)
	xs1, ts1 = smooth(x, 1.0, 1.0, 1.0)
	xs2, ts2 = smooth(x, 1.0, 1.0, 2.0)
	for i in range(20):
		print i, x[i], xk[i], xs0[i], xs1[i], xs2[i]
		assert numpy.alltrue( numpy.equal(numpy.less(x, 0.5),
						numpy.less(xk, 0.5)
						)
					)
		assert numpy.alltrue( numpy.equal(numpy.less(x, 0.5),
						numpy.less(xs0, 0.5)
						)
					)
		assert numpy.alltrue( numpy.equal(numpy.less(x, 0.5),
						numpy.less(xs1, 0.5)
						)
					)
		assert numpy.alltrue( numpy.equal(numpy.less(x, 0.5),
						numpy.less(xs2, 0.5)
						)
					)


def test2():
	x = numpy.zeros((500,), numpy.float)
	x[100:] = 1.0
	xs0, ts0 = smooth(x, 0.1, 1.0, 0.01)
	xs1, ts1 = smooth(x, 0.1, 1.0, 1.0)
	xs2, ts2 = smooth(x, 0.1, 1.0, 2.0)
	for i in range(200):
		if i%10 == 5:
			print i, x[i], xs0[i//10], xs1[i//10], xs2[i//10]
		else:
			print i, x[i]

def test3():
	x = numpy.zeros((200,), numpy.float)
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
