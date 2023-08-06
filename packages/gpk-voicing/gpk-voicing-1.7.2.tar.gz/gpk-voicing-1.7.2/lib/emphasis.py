#!/usr/bin/env python

"""Perceptual loudness measurement.
This is an implementation of
"Percieved Level of Noise by Mark VII and Decibels (E)"
S. S. Stevens,
J. Acoustical Soc. Am. v. 51(2, part 2) 1972
pages 575-602.

The algorithm matches the paper for FractOct==ThirdOct or OneOct.
The algorithm assumes that the level defined by SIXTY_EIGHT
corresponds to 68dB relative to 20 micro-Newtons per square meter
sound pressure.

USER INFORMATION:

You'll find, somewhere, a subdirectory named
speechresearch/voicing .
Within this is a script called emphasis_stevens.py .
This can be run as
python emphasis_stevens.py -o outputfile -write BITPIX=0 -c channelnumber inputfile
(there are a couple of other flags, too).

It will then read the input file (which is an audio recording)
and produce a time-series of the loudness.   Data input and
output is via the gpkio library, in .../speechresearch/gpkio.
That library has many virtues, but reading WAV files is not
one of them, so you have to convert .wav files to
the "GPK ASCII image" format (or one of several other formats),
using  .../speechresearch/lib/wavio.py .

The output will be in an ASCII version of the format,
which should be reasonably intelligible.    (The GPK ASCII image
format is based on the FITS astronomy format from NASA.)

However, that script uses the gpkio and gpklib libraries
(also under ../speechresearch).  These need to be compiled,
and it uses the gpk_img_python package that needs to be
installed via   "python setup.py install".
Oh, and .../speechresearch/gmisclib needs to be in
your PYTHONPATH.

Give it a try, and I'll be happy to help, and will
incorporate the troubles you have into some form of
documentation.    Sorry, I have nothing better yet.
"""

import math
from gmisclib import Num
from gmisclib import Numeric_gpk
from gmisclib import die
from gmisclib import gpkmisc

from gpk_voicing import voice_misc



FAC = 0.5
ThirdOct = 2.0**(1.0/3.0)
OneOct = 2.0
FracOct = 2.0**0.7
Fmax = 12500.0
Fmin = 50.0
NTOBF = int(round(math.log(Fmax/Fmin)/(math.log(FracOct)*FAC)))
EXFAC = 2
E = 0.3333

# 1.0 would cheat on the low frequency end a little.
TAUFAC = 1.2

# Fsum is correct at 68Db SOUND PRESSURE LEVEL AT 3150Hz
Fsum = 0.23*((1+math.log(FracOct)/math.log(ThirdOct))/2.0)

SIXTY_EIGHT = 6000.0
E = 0.3333

def frac_oct_ctr(i):
	return Fmin * (FracOct**i)


def frac_oct_hbw(i):
	return 0.5*(frac_oct_ctr(i+0.5) - frac_oct_ctr(i-0.5))

def calc_ear():
	"""At 68dB SPL."""
	F0 = 50.0
	app_A = [0.729, 1.33, 2.28, 2.92, 3.65, 4.47, 5.40,
		6.40, 7.48, 8.64, 8.64, 8.64, 8.64, 8.64, 8.64,
		10.1, 11.8, 13.7, 16.0, 16.0, 16.0, 16.0, 16.0,
		11.8, 8.64 ]
	o = Num.zeros((NTOBF,), Num.Float)
	for i in range(NTOBF):
		f = frac_oct_ctr(i*FAC)
		idx = math.log(f/F0)/math.log(FracOct)
		iidx = int(round(idx))
		# print i, f, iidx, len(app_A)
		assert iidx>=0 and iidx<len(app_A)
		fidx = idx - iidx
		if abs(fidx) < 0.01:
			o[i] = app_A[iidx]
		elif fidx < 0:
			assert i > 0
			o[i] = app_A[iidx]*(1-abs(fidx)) + app_A[iidx-1]*abs(fidx)
		else:
			assert i+1 < len(app_A)
			o[i] = app_A[iidx]*(1-abs(fidx)) + app_A[iidx+1]*abs(fidx)
	return o


def filter_fcn(f, fc, w):
	Exp = 6	# 18 dB/octave
	return 1.0/(((f-fc)/w)**Exp + 1)


_ff_cache = {}
def cached_filter_fcn(f, fc, w):
	key = (f.shape, fc, w)
	try:
		return _ff_cache[key]
	except KeyError:
		pass
	tmp = filter_fcn(f, fc, w)
	_ff_cache[key] = tmp
	return tmp

	

Ear = calc_ear()

def one_loud(d, extra):
	"""Approximate loudness of the sound in data array d.
	Extra contains misc. parameters."""

	n = d.shape[0]
	dt = extra['dt']
	assert d.shape == (n,)
	ss = Num.FFT.fft(Numeric_gpk.zero_pad_end(d*voice_misc.window(n, 0), EXFAC-1))
	ss[0] = 0	# Remove DC offset.
	# print "# ss.shape=", ss.shape
	f = Num.absolute(voice_misc.fft_freq(ss.shape[0], d=dt))
	assert abs(gpkmisc.N_maximum(f)-0.5/dt) < 0.05/dt
	loud = 0.0
	q = Num.zeros((NTOBF,), Num.Float)
	for i in range( NTOBF ):
		fc = frac_oct_ctr(i*FAC)
		w = frac_oct_hbw(i*FAC)
		q[i] = Num.sum(Num.absolute(ss * filter_fcn(f, fc, w))**2)
		# Fsig is now a bandpass filtered version of d.
	S = Ear * (q**E)
	Smax = S[Num.argmax(S)]
	Ssum = Num.sum(S)/FAC
	loud = Smax + Fsum*(Ssum - Smax)
	return loud




def one_emphasis(t, data, extra, DT):
	"""Measure the loudness near time t."""
	s, e = voice_misc.start_end(t*DT, extra['dt'], extra['window'], data.shape[0])
	d = data[s:e]
	f1 = one_loud(d, extra)
	# print "# t=", t*DT, "s, e=", s, e, "loudness=", f1
	return f1


def emphasis(data, extra, DT=0.01):
	"""Measure the time-series of loudness of a data array data.
	DT is the sampling interval for the resulting loudness time series."""
	ns = int(math.floor(extra['dt']*data.shape[0]/DT))
	o = Num.zeros((ns,), Num.Float)
	for t in range(ns):
		o[t] = one_emphasis(t, data, extra, DT)
	return o


def simple_emphasis(data, dt, DT = 0.01):
	extra = {'dt': dt}
	wmin = 2*frac_oct_hbw(0)
	# Ideally, we'd use a different window size for each frequency...
	taumax = max(TAUFAC / wmin, 1.5*DT)
	extra['window'] = voice_misc.near_win_size(near=taumax/dt, tol=0.1*taumax/dt)
	# print 'win', extra['window'], taumax/dt, wmin, frac_oct_hbw(0), frac_oct_ctr(0)
	return emphasis(data/SIXTY_EIGHT, extra, DT)


