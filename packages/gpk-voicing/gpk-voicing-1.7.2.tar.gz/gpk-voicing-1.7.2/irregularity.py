#!/usr/bin/env python

"""This script produces a measure of the irregularity of
a waveform.  It is zero if the waveform is precisely periodic.
It is approximately 1 for white noise.

This is used as the aperiodicity measure in
Kochanski, Coleman, Grabe and Rosner JASA 2005.
"""

import sys
import math as M
import numpy
from gmisclib import die
from gpk_voicing import power
import gpkimgclass
from gpk_voicing import voice_misc

DELTA_DELAY = 1.0/(2400.0 * 2 * M.pi)
# DELTA_DELAY is chosen so that we can align the oscillations
# at the first formant (f1 is normally under 1200 Hz)
# to an accuracy of 1 radian or less.

Fmin = 50.0
Fmax = 500.0
Fhp = 500.0
WINDOW = 0.020

BLOCK_EDGE = 0.1	# Seconds

DBG = None

# def one_predict(d, delay, dt, Dt):
	# zl = Num.zeros((delay/2,), Num.Float)
	# zr = Num.zeros((delay-delay/2,), Num.Float)
	# dtmp = Num.concatenate( (zl, d, zr) )
	# tmp = dtmp[delay:] - dtmp[:-delay]
	# assert tmp.shape == d.shape
	# return power.smooth(tmp*tmp, dt, Dt, extra=WINDOW)


def predict_err(d, delays, dt, Dt):
	global WINDOW
	assert min(delays) >= 0
	mxdelay = max(delays)//2 + 1
	n = d.shape[0]
	ze = numpy.zeros((mxdelay,))
	dtmp = numpy.concatenate( (ze, d, ze) )
	del d	# save memory.
	o = None
	for delay in delays:
		dlh = delay//2
		dlH = delay - dlh
		ddtmp = dtmp[ mxdelay+dlh : mxdelay+dlh+n ] - dtmp[ mxdelay-dlH : mxdelay-dlH+n ]
		assert ddtmp.shape[0] == n, "Shapes do not match: %s and %s" % (ddtmp.shape, n)
		tmp, t0 = power.smooth(ddtmp**2, dt, Dt, extra=WINDOW)
		if DBG:
			DBG.plot(tmp)
		if o is None:
			o = tmp
		else:
			numpy.minimum(o, tmp, o)
	if DBG:
		DBG.show()
	return o


def local_power(d, dt, Dt):
	global WINDOW
	return power.smooth(d**2, dt, Dt, extra=WINDOW)


def fractional_step_range(initial, final, step=1):
	"""Generates an array of window offsets.
	No two offsets are equal, and they are integers
	between initial and final."""

	assert step != 0
	if step < 0:
		return fractional_step_range(initial, final, -step)
	if final < initial:
		return []
	o = []
	tmp = float(initial)
	assert tmp > 0.5, "Initial=%g too close to zero, or even negative!" % tmp
	ilast = 0
	while tmp <= final:
		itmp = int(round(tmp))
		if itmp != ilast and itmp>=initial:
			o.append(itmp)
		ilast = itmp
		tmp += step
	return o


def aperiodicity(d, dt, Dt):
	if Fmin*dt > 0.5 or Fmin*dt<1.0/d.shape[0]:
		die.warn("Silly time scale")
	die.info("Hipass at %f" % (Fmin*dt))
	d = voice_misc.hipass_sym_butterworth(d, Fmin*dt)
	d = voice_misc.hipass_first_order(d, Fhp*dt)
	if DBG is not None:
		DBG.plot(numpy.arange(d.shape[0])*dt, d, 'k-')
		DBG.title('filtered signal')
	p, tshift = local_power(d, dt, Dt)
	if DBG is not None:
		DBG.figure()
		DBG.plot(tshift+numpy.arange(p.shape[0])*Dt, p)
		DBG.title('Local power')
		DBG.show()
	assert tshift < Dt
	imin = 1.0/(dt * Fmax)
	imax = 1.0/(dt * Fmin)
	istep = DELTA_DELAY/dt
	delays = fractional_step_range(imin, imax, istep)
	perr = predict_err(d, delays, dt, Dt)
		# The factor of 2.0 below is because perr is a difference
		# of two signals.  If they were independent random noise,
		# then the variances would add, so that perr=2*p for
		# white noise.
		# In other words, this measure goes to 1 for white noise,
		# and to zero for a periodic signal.
	assert perr.shape == p.shape
	return (tshift, numpy.sqrt(perr/(2.0*p)))


def  block_aperiodicity(data, dt, Dt, blocksize=6.0):
	if blocksize is None:
		return aperiodicity(data, dt, Dt)
	assert BLOCK_EDGE >= Dt
	blocksize = Dt * int(round(blocksize/Dt))
	assert blocksize > BLOCK_EDGE
	m = data.shape[0]
	ntau = int(M.ceil(m*dt/blocksize))
	nout = int(M.ceil(m*dt/Dt))
	pad = int(round(Dt*round(BLOCK_EDGE/Dt)/dt))

	irr = None
	tshift = None
	S0 = 0.0
	e = 0
	for i in range(ntau):
		s0 = int(round((m*i)/float(ntau)))
		se = int(round((m*(i+1))/float(ntau)))
		ps0 = max(0, s0-pad)
		pse = min(m, se+pad)
		ttshift, x = aperiodicity(data[ps0:pse], dt, Dt)
		if tshift is None:
			tshift = ttshift
		if irr is None:
			irr = numpy.zeros((nout+1,))
		tau0 = int(M.floor((s0-ps0)*(dt/DT)))
		nS = min((se-s0)*(dt/DT), x.shape[0]-tau0)
		inS = int(M.ceil(nS))
		iS0 = int(M.floor(S0))
		assert iS0+inS <= nout, "S0=%.1f nS=%.1f S0+nS=%.1f nout=%d" % (S0, nS, S0+nS, nout)
		# print 'irr', irr.shape, iS0, iS0+inS, 'x=', x.shape, tau0, tau0+inS
		irr[iS0:iS0+inS] = x[tau0:tau0+inS]
		S0 += nS
		e = iS0+inS
	assert nout-2 <= e <= nout+1, "e=%d nout=%d" % (e, nout)
	return (tshift, irr[:e])


def test(pylab):
	import random
	DT = 0.01
	dt = 1.0/random.normalvariate(16000.0, 1000.0)
	L = random.expovariate(1.0/15.0)
	n = int(round(L/dt))
	signal = numpy.random.normal(0.0, 0.1, size=(n,))
	step = int(round(2.0/dt))
	k = int(round(0.5/dt))
	omega = 2*M.pi*100.0
	i = 0
	while i < n:
		kk = min(k, n-i)
		signal[i:i+kk] = numpy.sin(numpy.arange(kk)*dt*omega)
		if i+k < n:
			kk = min(k, n-i-k)
			signal[i+k:i+k+kk] = numpy.random.normal(0.0, 0.9, size=(kk,))
		i += step
	
	if pylab:
		pylab.plot(numpy.arange(signal.shape[0])*dt, signal)
	tshift, o = block_aperiodicity(signal, dt, DT)
	x = numpy.arange(o.shape[0])*DT + tshift
	if pylab:
		pylab.plot(x, o)
		pylab.show()



if __name__ == '__main__':
	DT = 0.01	# Seconds.  Default output sampling interval.
	arglist = sys.argv[1:]
	Blocksize = 10.0
	arglist0 = arglist
	column = None
	signalfile = None
	outfile = None
	extrahdr = {}
	while arglist and arglist[0].startswith('-'):
		arg = arglist.pop(0)
		if arg == '--':
			break
		elif arg == '-params':	# For optimization purposes
			Fmin = atof(arglist.pop(0))
			Fmax = atof(arglist.pop(0))
			Fhp = atof(arglist.pop(0))
			WINDOW = atof(arglist.pop(0))
		elif arg == '-dt':
			DT = float(arglist.pop(0))
		elif arg == '-f':
			signalfile = arglist.pop(0)
		elif arg == '-c':
			tmp = arglist.pop(0)
			try:
				column = int( tmp )
			except ValueError:
				column = tmp
		elif arg == '-b':
			Blocksize = float(arglist.pop(0))
			if Blocksize <= 0.0:
				Blocksize = None
		elif arg == '-d':
			import pylab as DBG
		elif arg == '-test':
			test(None)
			sys.exit(0)
		elif arg == '-Test':
			import pylab
			test(pylab)
			sys.exit(0)
		elif arg == '-o':
			outfile = arglist.pop(0)
		elif arg == '-write':
			extrahdr = dict( [q.strip().split('=', 1)
					for q in arglist.pop(0).split(';') ]
					)
		else:
			die.info("Unrecognized flag: %s" % arg)
			print __doc__
			die.exit(1)
	if arglist and signalfile is None:
		signalfile = arglist.pop(0)
	if arglist and outfile is None:
		outfile = arglist.pop(0)
	elif outfile is None:
		outfile = 'pdur.dat'
	if column is None:
		column = 0
	if signalfile is None:
		die.info("No signal file specified.")
		print __doc__
		die.exit(1)
	if arglist:
		die.info('Extra arguments!')
		print __doc__
		die.exit(1)
	signal = gpkimgclass.read(signalfile)
	try:
		signal.column(column)
	except KeyError:
		die.info("File has %d columns" % signal.n[1])
		die.die("Bad column: %s" % str(column))

	tshift, o = block_aperiodicity(signal.column(column), signal.dt(), DT,
					blocksize=Blocksize)

	hdr = signal.hdr.copy()
	hdr['program'] = sys.argv[0]
	hdr['ARGV'] = arglist0
	hdr['input_file'] = signalfile
	hdr['column'] = column
	hdr['CDELT2'] = DT
	hdr['CRPIX2'] = 1
	hdr['CRVAL2'] = signal.start() + tshift
	hdr['CRPIX1'] = 1
	hdr['CDELT1'] = 1
	hdr['TTYPE1'] = 'aperiodicity'
	hdr['BITPIX'] = -32
	hdr['DataSamplingFreq'] = 1.0/signal.dt()
	hdr.update( extrahdr )
	gpkimgclass.gpk_img(hdr, o).write(outfile)
