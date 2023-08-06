#!/usr/bin/env python

import math
import numpy
from gmisclib import Num
from gmisclib import ortho_poly
from gmisclib import die
from gmisclib import gpkmisc

from gpk_voicing import gammatone as GT


_wincache = {}
_WIN_CACHE_SIZE = 20

def window(n, k, norm=2):
	"""Make a window of length n with k nodes.
	The window is normalized so that Num.sum(w**2)==1."""

	assert n > 0
	assert k >= 0
	cachekey = (n,k,norm)
	if cachekey in _wincache:
		return _wincache[ cachekey ]

	opn = ortho_poly.Chebyshev(n)
	# opn.x ranges over (-1, 1)
	w = (1 + numpy.cos(opn.x*math.pi)) * opn.P(k)
	if norm > 0:
		numpy.divide(w, (numpy.sum(numpy.absolute(w)**norm))**(1.0/norm), w)
	while len(_wincache) > _WIN_CACHE_SIZE:
		_wincache.popitem()
	_wincache[ cachekey ] = w
	return w


def cont_kernel(n, k, norm=2):
	"""Make a window with width n,
	except that it changes continuously when n
	is a floating point number.   The resulting window is
	always an odd length.
	"""
	assert n > 0
	n2 = n/2.0
	nu = 2*int(math.ceil(n2)) + 1
	nl = 2*int(math.floor(n2)) + 1
	assert nu == nl+2
	f = n2 - math.floor(n2)
	w = window(nu, k, norm=norm) * f
	numpy.add(w[1:-1], window(nl, k, norm=norm)*(1-f), w[1:-1])
	if norm > 0:
		numpy.divide(w, (numpy.sum(numpy.absolute(w)**norm))**(1.0/norm), w)
	return w


def xexp(a):
	"""exp(a), except protected from underflows."""
	MIN = -100
	ok = Num.greater(a, MIN)
	return ok * Num.exp(Num.maximum(a, MIN))




def start_end(t, dt, window, len_d):
	"""Find start and end points for a window.
	t = desired window center (seconds).
	window = window width (in samples).
	dt = sampling rate (seconds).
	len_d = length of data array (samples).
	"""
	assert type(window) == type(1)
	# window = int(round(window/dt))
	s = int(round(t/dt - 0.5*window))
	if s < 0:
		s = 0
	elif s+window > len_d:
		s = len_d - window
	e = s + window
	return (s, e)


def _filter_win_size(n, cutoff_freq):
	np = n + max(10.0/cutoff_freq, n*0.01)
	nx = near_win_size(min=np+1, tol=1+n//11, real=True)
	return nx - nx%2



_fftworkcache = {}
def _fftwork(n):
	"""This estimates the work required to compute a FFT of size N,
	using the Cooley-Tukey algorithm.
	See http://en.wikipedia.org/wiki/Cooley-Tukey_FFT_algorithm
	"""
	try:
		return _fftworkcache[n]
	except KeyError:
		pass
	f1 = gpkmisc.a_factor(n)
	if f1 == n:
		tmp = n**2
	else:
		nof1 = n/f1
		tmp = f1*_fftwork(nof1) + n + nof1*_fftwork(f1)
	_fftworkcache[n] = tmp
	return tmp


def _fftwork_real(n):
	"""This is the work for a forward and reverse transform of
	real data back to real data, using Num.FFT.rfft and Num.FFT.irfft
	"""
	return _fftwork(n) + _fftwork(n-n%2)


def near_win_size(near=None, tol=None, min=None, max=None, real=False):
	"""Find a window size near the specified size where
	the FFT algorithm is fastest."""

	if near is not None and tol is not None:
		nmax = int(round(near + tol))
		nmin = int(round(near - tol))
	elif min is not None and max is not None:
		nmax = int(round(max))
		nmin = int(round(min))
	elif min is not None and tol is not None:
		nmin = int(round(min))
		nmax = int(round(min + tol))
	elif max is not None and tol is not None:
		nmax = int(round(max))
		nmin = int(round(max - tol))
	else:
		raise ValueError, "Needs near&tol, min&max, min&tol, or max&tol."

	if real:
		fftwork = _fftwork_real
	else:
		fftwork = _fftwork

	besti = nmin
	bestwork = fftwork(besti)
	Since_lim = 100
	since = 0
	for i in range(nmin, nmax+1):
		t = fftwork(i)
		if t < bestwork:
			bestwork = t
			besti = i
			since = 0
		else:
			# This branch is just to keep near_win_size
			# from trying too hard.   Otherwise, it's quite
			# possible to spend more time finding the optimal
			# size than one spends taking the actual FFT.
			since += 1
			if since > Since_lim:
				break
	return besti


def near_win_size_real(near=None, tol=None, min=None, max=None):
	return near_win_size(near, tol, min, max, real=True)


def test_win_size():
	assert near_win_size(min=4, max=7) == 4
	assert near_win_size(min=5, max=7) != 7
	assert near_win_size(near=15, tol=2) != 17
	assert near_win_size(near=14, tol=1) != 13
	assert near_win_size(near=97, tol=1) != 97
	assert near_win_size(near=197, tol=1) != 197
	assert near_win_size(near=23, tol=1) != 23


def test_print_win():
	N = 100
	w0 = window(N, 0)
	w1 = window(N, 1)
	w2 = window(N, 2)
	w3 = window(N, 3)
	w4 = window(N, 4)
	w5 = window(N, 5)
	for i in range(N):
		print i, w0[i], w1[i], w2[i], w3[i], w4[i], w5[i]



# def hipass_first_order(d, cutoff_freq):
	# """A first-order high-pass filter.
	# Cutoff freq is measured in cycles per point."""
# 
	# assert cutoff_freq >= 0.0
	# assert len(d.shape) == 1
	# n = d.shape[0]
	# nx = _filter_win_size(n, cutoff_freq)
	# dx = Num.FFT.rfft(d, nx)
	# f = real_fft_freq(dx.shape[0])
	# fr = 1j* (f / cutoff_freq)
	# ff = fr / (1 + fr)
	# ff[0] = ff[0].real
	# ff[-1] = ff[-1].real
	# return Num.FFT.irfft(dx*ff, nx)[:n]
# 
# 
# def lopass_first_order(d, cutoff_freq):
	# """A first-order low-pass filter.
	# Cutoff freq is measured in cycles per point."""
# 
	# assert cutoff_freq >= 0.0
	# assert len(d.shape) == 1
	# n = d.shape[0]
	# nx = _filter_win_size(n, cutoff_freq)
	# dx = Num.FFT.rfft(d, nx)
	# f = real_fft_freq(dx.shape[0])
	# fr = 1j* (f / cutoff_freq)
	# ff = 1 / (1 + fr)
	# ff[0] = ff[0].real
	# ff[-1] = ff[-1].real
	# return Num.FFT.irfft(dx*ff, nx)[:n]

hipass_first_order = GT.hipass_first_order
lopass_first_order = GT.lopass_first_order


def bandpass_first_order(d, cutoff_hp, cutoff_lp):
	"""A combinatio of a first-order high-pass filter
	and a low-pass filter.
	Cutoff freq is measured in cycles per point."""

	assert cutoff_lp >= 0.0
	assert cutoff_hp >= 0.0
	assert len(d.shape) == 1
	n = d.shape[0]
	nx = _filter_win_size(n, 1.0/math.hypot(1.0/cutoff_lp, 1.0/cutoff_hp))

	dx = Num.FFT.rfft(d, nx)
	f = real_fft_freq(dx.shape[0])

	frlp = 1j* (f / cutoff_lp)
	frhp = 1j* (f / cutoff_hp)
	ff = frhp / ((1 + frhp)*(1+frlp))
	ff[0] = ff[0].real
	ff[-1] = ff[-1].real
	return Num.FFT.irfft(dx*ff, nx)[:n]


def test_hpf():
	q = Num.cos(Num.arrayrange(10000)*0.003*2*math.pi)
	sq = Num.sum(q*q)
	q1 = hipass_first_order(q, 0.0003)
	sq1 = Num.sum(q1*q1)
	assert 0.98*sq < sq1 < 0.995*sq
	q4 = hipass_first_order(q, 0.003)
	sq4 = Num.sum(q4*q4)
	assert 0.4*sq < sq4 < 0.6*sq
	q5 = hipass_first_order(q, 0.03)
	sq5 = Num.sum(q5*q5)
	# print sq5/sq
	assert  0.003 < sq5 < 0.03*sq




def fft_freq(n, d=1.0):
	"""Returns an array of indices whose frequencies are between f0 and f1
	after you've called fft().
	This will produce negative values where appropriate.
	"""
	if hasattr(Num.FFT, 'fftfreq'):
		return Num.FFT.fftfreq(n, d)
	fidx = Num.arrayrange(n)
	fneg = fidx - n
	useneg = Num.less(-fneg, fidx)
	df = 0.5/(n*d)
	return df * Num.where(useneg, fneg, fidx)


def fft_indices(f0, f1, n, d=1.0):
	"""Returns an array of indices whose frequencies are between f0 and f1
	after you've called real_fft().
	"""
	raise RuntimeError, "Sorry! Not implemented"


def real_fft_freq(n, d=1.0):
	"""Returns the frequencies associated with an index, after you've
	called real_fft().
	@param n: the size of the transformed array (i.e. frequency domain, complex)
	@type n: int
	@rtype: numpy.ndarray
	@return: the frequency associated with each element in a Fourier Transform
	"""
	fidx = Num.arrayrange(n)
	df = 0.5/(n*d)
	return df * fidx


def real_fft_indices(f0, f1, n, d=1.0):
	"""Returns the indices whose frequencies are between f0 and f1
	after you've called real_fft().
	"""
	df = 0.5/(n*d)
	f0 = max(0.0, f0)
	imin = int(math.ceil(f0/df))
	imax = int(math.floor(f1/df))
	return (imin, imax+1)



def dataprep_flat_real(data, dt, edgewidth, pad=None):
	return dataprep_flat_generic(data, dt, edgewidth, pad, True)

def dataprep_flat(data, dt, edgewidth, pad=None):
	return dataprep_flat_generic(data, dt, edgewidth, pad, False)


def dataprep_flat_generic(data, dt, edgewidth, pad, isreal):
	"""Pad the data, subtract the average, and round
	the edges of the window.
	"""
	m = data.shape[0]
	if pad is None:
		pad = 2*edgewidth + m//10
	min_win_size = m + pad
	n = near_win_size(min=min_win_size, tol=m//11 + 1, real=isreal)
	d = Num.zeros((n,), Num.Float)
	avg = Num.average(data)
	d[:m] = data - avg
	nedge = int(round(edgewidth/dt))
	assert nedge <= m
	ew = 0.5*(1.0-Num.cos((math.pi/nedge)*(Num.arrayrange(nedge)+0.5)))
	Num.multiply(d[:nedge], ew, d[:nedge])
	Num.multiply(d[m-nedge:m], ew[::-1], d[m-nedge:m])
	return d


def lowpass_sym_butterworth(d, cutoff_freq, order=4):
	"""A time-symmetric filter with a magnitude response that
	is the same as the Butterworth filter.
	Cutoff freq is measured in cycles per point."""
	assert len(d.shape) == 1
	if cutoff_freq<=0 or cutoff_freq>10.0:
		die.warn('Silly value of cutoff_freq: %g cycles per point.' % cutoff_freq)
	n = d.shape[0]
	nx = _filter_win_size(n, cutoff_freq)
	dx = Num.FFT.rfft(d, nx)
	f = real_fft_freq(dx.shape[0])
	ff = Num.sqrt(1.0/(1 + (f/cutoff_freq)**(2*order)))
	return Num.FFT.irfft(dx*ff, nx)[:n]




def lowpass_sym_Gaussian(d, cutoff_freq):
	"""A time-symmetric filter with a Gaussian impulse response.
	Cutoff freq is measured in cycles per point.
	"""
	assert len(d.shape) == 1
	if cutoff_freq<=0 or cutoff_freq>10.0:
		die.warn('Silly value of cutoff_freq: %g cycles per point.' % cutoff_freq)
	n = d.shape[0]
	nx = _filter_win_size(n, cutoff_freq)
	dx = Num.FFT.rfft(d, nx)
	f = real_fft_freq(dx.shape[0])
	q = 1.0/(2*cutoff_freq**2)
	ff = Num.exp(-f**2 * q)
	return Num.FFT.irfft(dx*ff, nx)[:n]

lowpass_sym_gaussian = lowpass_sym_Gaussian



def hipass_sym_butterworth(d, cutoff_freq, order=4):
	"""A time-symmetric filter with a magnitude response that
	is the same as the Butterworth filter.
	Cutoff freq is measured in cycles per point."""
	assert len(d.shape) == 1
	if cutoff_freq<=0 or cutoff_freq>10.0:
		die.warn('Silly value of cutoff_freq: %g cycles per point.' % cutoff_freq)
	n = d.shape[0]
	nx = _filter_win_size(n, cutoff_freq)
	dx = Num.FFT.rfft(d, nx)
	f = real_fft_freq(dx.shape[0])
	ff1 = (f/cutoff_freq)**(2*order)
	ff = Num.sqrt( ff1 / (1 + ff1) )
	return Num.FFT.irfft(dx*ff, nx)[:n]


def test_lpb():
	q = Num.cos(Num.arrayrange(10000)*0.003*2*math.pi)
	sq = Num.sum(q*q)
	q1 = lowpass_sym_butterworth(q, 0.1)
	sq1 = Num.sum(q1*q1)
	# print sq1/sq
	assert 0.99*sq < sq1 < 1.00001*sq
	q2 = lowpass_sym_butterworth(q, 0.05)
	sq2 = Num.sum(q2*q2)
	# print sq2/sq
	assert 0.99*sq < sq2 < 1.00001*sq
	q4 = lowpass_sym_butterworth(q, 0.003)
	sq4 = Num.sum(q4*q4)
	# print sq4/sq
	assert 0.4*sq < sq4 < 0.6*sq
	q5 = lowpass_sym_butterworth(q, 0.001)
	sq5 = Num.sum(q5*q5)
	# print sq5/sq
	assert  0 < sq5 < 0.2*sq
	

def test_hpb():
	q = Num.cos(Num.arrayrange(10000)*0.003*2*math.pi)
	sq = Num.sum(q*q)
	q1 = hipass_sym_butterworth(q, 0.0003)
	sq1 = Num.sum(q1*q1)
	# print sq1/sq
	assert 0.99*sq < sq1 < 1.00001*sq
	q4 = hipass_sym_butterworth(q, 0.003)
	sq4 = Num.sum(q4*q4)
	# print sq4/sq
	assert 0.4*sq < sq4 < 0.6*sq
	q5 = hipass_sym_butterworth(q, 0.03)
	sq5 = Num.sum(q5*q5)
	# print sq5/sq
	assert  0 < sq5 < 0.2*sq


def pink_noise(n):
	"""Create pink noise where the power spectral density
	goes as 1/f (except right at f=0).
	"""
	m = near_win_size_real(near=2*n+2, tol=n//3+1)

	rtmp = Num.RA.standard_normal(m)
	itmp = Num.RA.standard_normal(m)
	tmp = rtmp + 1j*itmp
	f = real_fft_freq(m)
	assert f[0] == 0.0
	tmp[0] = 0.0
	f[0] = 1.0
	Num.multiply(tmp, 1.0/Num.sqrt( f ), tmp)
	return Num.FFT.inverse_real_fft(tmp)[:n]

if __name__ == '__main__':
	test_win_size()
	test_print_win()
	test_hpf()
	test_lpb()
	test_hpb()
