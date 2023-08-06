#!/usr/bin/env python

"""Perceptual spectrum for speech."""

import sys
import math as M
from gmisclib import erb_scale
from gmisclib import gpkmisc
from gmisclib import die

import numpy

# import wavio
# import gpkimgclass

pylab = None

import gpk_voicing.voice_misc as VM
from gpk_voicing import power
from gpk_voicing import percep_spec_extras as PS
from gpk_voicing import gammatone

CBmax = erb_scale.f_to_erb(8000.0)
CBmin = erb_scale.f_to_erb(50.0)
BBSZ = 0.5
E = 0.333
Neural_Tick = 1e-4	# The best possible time resolution of the auditory
			# system.  (E.g. from binaural direction measurements.)
DISS_BWF = 0.25
MAX_DISS_FREQ = 250.0
HP_DISS_FREQ = 30.0
BLOCK_EDGE = 0.3	# Seconds

# def SafeExp(x):
	# return Num.exp(Num.maximum(-200.0, x))


def tau_lp(fc):
	"""This is the cutoff frequency of the modulation transfer function
	in the ear, as a function of frequency.
	From R. Plomp and M. A. Bouman, JASA 31(6), page 749ff, June 1959
		'Relation of hearing threshold and duration of tone pulses'
		"""
	Tau200 = 0.4
	Tau10k = 0.13
	tmp = Tau200 + (M.log(fc/200.0)/M.log(1e4/200.0))*(Tau10k-Tau200)
	assert tmp>0
	return tmp


def cochlear_filter(fofc):
	"""Transfer function taken from "Improved Audio Coding Using a
	Psychoacoustic Model Based on a Cochlear Filter Bank
	IEEE Transactions of Speech and Audio Processing, 10(7) October 2002,
	Pages 495-503.  au=Frank Baumgarte.
	"""
	Q = 4.0
	Slp = 25.0/(20.0*M.log10(1.2))
	Shp = 8.0/(20.0*M.log10(1.2))
	fofc_Shp = fofc**Shp
	return (fofc_Shp) / ( (1+fofc**Slp) * (1 + (1j/Q)*(fofc**(Shp/2))
				- fofc_Shp)
				)


def threshold(f):
	"""IN pressure amplitude.
	Crudely taken from Handbook of Perception vol 4: hearing,
	E.C.Carterette and M.P.Friedman, editors,
	Academic Press 1978, isbn 0-12-161904-4.
	Curve near 70db used."""
	return M.sqrt((200.0/f)**4 + 1 + (f/8000.0)**16)


def accum_abs_sub(a, b, o):
	"""This does a little computation in a block-wise fashion
	to keep all the data witin the processor's cache.
	It computes sum( abs(a-b) ).
	"""
	BKS = 6000
	n = o.shape[0]
	assert a.shape == (n,)
	assert b.shape == (n,)
	assert o.shape == (n,)
	tmp = numpy.zeros((BKS,), numpy.float)
	for i in range(0, n, BKS):
		e = min(i+BKS, n)
		tmpi = tmp[:e-i]
		ai = a[i:e]
		bi = b[i:e]
		oi = o[i:e]
		numpy.subtract(ai, bi, tmpi)
		numpy.absolute(tmpi, tmpi)
		numpy.add(oi, tmpi, oi)
	return o


def list_accum_abs_sub_dly(tk, dly):
	lng = tk[0][dly:].shape[0]
	o = numpy.zeros((lng,), numpy.float)
	for tkd in tk:
		a = tkd[:-dly]
		b = tkd[dly:]
		accum_abs_sub(a, b, o)
	return o



def process_voicing(tk, tick, Dt):
	"""@param Dt: the sampling rate of the output vectors.
	@type Dt: C{float}
	@param tick: the sampling rate of the vectors in C{tk}.
	@type tick: C{float}
	@param tk: a list of vectors, each of which represents the neural firing
		of a particular point in the cochlea.
	@type tk: [ numpy.ndarray, ...]
	@return: (avg, min) where avg-min is the voicing estimator.
		avg: C{float}, min: C{float}
	"""
	LOWF = 50.0
	HIGHF = 400.0
	lowf = int(round(1.0/(tick*LOWF)))
	highf = int(round(1.0/(tick*HIGHF)))
	tmps = None
	tmpmin = None
	## tmpss = None
	tmpn = 0
	for dly in range(highf, lowf):
		# dhl = dly//2
		# dhr = dly - dhl
		# dlytmp = list_accum_abs_sub_dly(tk, dly)
		dlytmp = PS.list_accum_abs_sub_dly(tk, dly)
		assert len(dlytmp.shape) == 1
		# al = Num.zeros((dhl,), Num.Float)
		# ar = Num.zeros((dhr,), Num.Float)
		# dlytmp = Num.concatenate((al, dlytmp, ar))
		tmp2, t0 = power.smooth(dlytmp, tick, Dt, extra=1.0/(LOWF*M.sqrt(12.0)))

		if tmps is None:
			tmpn = 1
			tmps = tmp2
			tmpmin = numpy.array(tmp2, copy=True)
		else:
			tmpn += 1
			numpy.add(tmps, tmp2, tmps)
			numpy.minimum(tmpmin, tmp2, tmpmin)
	return (tmps, tmpn, tmpmin)


class roughness_c(object):
	"""This should be based on Hutchinson and KNopoff 1978
	Kameoka an Kuriygawa 1969a; Viemeister 1988;
	Aures 1985; Plomp and Levelt 1965.
	But it isn't yet.

	Hutchinson W. and Knopoff, L. 1978 The acoustic componenet of
	Western consonance.  Interface 7, 1-29.
	
	Kameoka and Kuriygawa 1969.  Consonance Theory: Part 1.
	J. Acoustical Soc. America. 45 1451-1458
	(and 1459-1469 for part II).

	Viemeister, N. F. 1977 Temporal factors in audition: A system
	analysis approach.   In E. F. Evans and J. P. Wilson (eds)
	Psychophysics and physiology of hearing (pp. 419-429)
	London: Academic Press

	Aures, W. 1985 Ein Berechnun gsverfahren der Rauhigkeit
	[A roughness calculation method] Acustica 58 268-281

	Plomp R. and Levelt W. 1965 Tonal consonance and critical
	bandwidth.  JASA 38, 548-560.
	"""
	def __init__(self):
		self.y = None
		self.n = 0
		self.dt = None
	
	def add(self, y, dt, diss_bw):
		if self.dt is None:
			assert dt > 0
			self.dt = dt
		else:
			assert abs(dt-self.dt) < 0.0001*self.dt
		tmp = VM.lowpass_sym_butterworth(y, diss_bw*dt)
		tmp = VM.hipass_first_order(tmp, HP_DISS_FREQ*dt)
		tmp = numpy.absolute(tmp)
		# if pylab:
			# print 'roughness_c.add', numpy.average(tmp), diss_bw
			# pylab.plot(tmp)
		if self.y is None:
			self.y = tmp
		else:
			numpy.add(self.y, tmp, self.y)
		self.n += 1

	def get(self, Dt):
		# if pylab:
			# pylab.figure()
		yfilt, t0 = power.smooth(self.y, self.dt, Dt)
		# if pylab:
			# pylab.plot(yfilt)
			# pylab.show()
		return yfilt*(0.1/self.n)


class peakalign_c(object):
	def __init__(self):
		self.y = None
		self.shifts = []
		self.dbg = []
		self.n = 0
		self.dt = None

	EDGE = 700
	
	def add(self, y, dt, fc):
		if self.dt is None:
			assert dt > 0
			self.dt = dt
		else:
			assert abs(dt-self.dt) < 0.0001*self.dt
		FF = -3.2
		sh = int(round(FF/(dt*fc))) + self.EDGE
		if self.y is None:
			self.y = numpy.zeros((y.shape[0]+2*self.EDGE,))
		numpy.add(self.y[sh:sh+y.shape[0]], y, self.y[sh:sh+y.shape[0]])
		if pylab and fc>400:
			self.dbg.append(y)
			self.shifts.append(sh)
		self.n += 1


	def get(self, Dt):
		if pylab:
			for (i, (y,sh)) in enumerate(zip(self.dbg, self.shifts)):
				xpl = []
				ypl = []
				for dly in range(-100,100):
					ypl.append(numpy.sum(y*self.y[sh+dly:sh+y.shape[0]+dly]))
					xpl.append(dly)
				pylab.plot(xpl, [q/max(ypl) for q in ypl], linestyle='-',
						color=(float(i)/float(self.n), 0.5, float(self.n-i)/float(self.n)))
		if pylab:
			pylab.show()
		cfilt, t0 = power.smooth(self.y*self.y, self.dt, Dt)
		return cfilt/self.n**2


def block_percep_spec(data, dt, Dt, **kwargs):
	"""This computes the perceptual spectrum in blocks and glues them
	together.   It's useful when the data is too large to fit in memory.
	"""
	if kwargs.get('blocksize', None) is None:
		return perceptual_spec(data, dt, Dt, **kwargs)
	assert BLOCK_EDGE >= Dt
	blocksize = Dt * int(round(kwargs['blocksize']/Dt))
	del kwargs['blocksize']
	assert blocksize > BLOCK_EDGE
	m = data.shape[0]
	ntau = int(M.ceil(m*dt/blocksize))
	nout = int(M.ceil(m*dt/Dt))
	pad = int(round(Dt*round(BLOCK_EDGE/Dt)/dt))

	neural = None
	tshift = None
	bctrs = None
	S0 = 0.0
	e = 0
	for i in range(ntau):
		s0 = int(round((m*i)/float(ntau)))
		se = int(round((m*(i+1))/float(ntau)))
		ps0 = max(0, s0-pad)
		pse = min(m, se+pad)
		tbc, x, ttshift = perceptual_spec(data[ps0:pse], dt, Dt, **kwargs)
		if tshift is None:
			tshift = ttshift
		if bctrs is None:
			bctrs = tbc
		else:
			assert tbc == bctrs
		if neural is None:
			neural = numpy.zeros((x.shape[0], nout+1), numpy.float)

		tau0 = int(M.floor((s0-ps0)*(dt/Dt)))
		nS = min((se-s0)*(dt/Dt), x.shape[1]-tau0)
		# print 'dt=', dt, "Dt=", Dt
		# print 'nS=', nS, "min(", (se-s0)*(dt/Dt), x.shape[0]-tau0, ")"
		inS = int(M.ceil(nS))
		iS0 = int(M.floor(S0))
		assert iS0+inS <= nout, "S0=%.1f nS=%.1f S0+nS=%.1f nout=%d" % (S0, nS, S0+nS, nout)
		# print 'neural', neural.shape, iS0, iS0+inS, 'x=', x.shape, tau0, tau0+inS
		neural[:, iS0:iS0+inS] = x[:, tau0:tau0+inS]
		# print 'S0=', S0, '->', S0+nS
		S0 += nS
		e = iS0+inS
		# print 'e=', e
	assert nout-2 <= e <= nout+1, "e=%d nout=%d" % (e, nout)
	return (bctrs, neural[:,:e], tshift)


class fft_filterbank(object):
	def __init__(self, data, dt, Dt):
		self.d = VM.dataprep_flat_real(data, dt, Dt)
		self.ss = numpy.fft.real_fft( self.d )
		self.f = numpy.absolute(VM.real_fft_freq(self.ss.shape[0], d=dt))

	def filter(self, fc):
		xferfcn = cochlear_filter(self.f/fc)
		xferfcn[0] = xferfcn[0].real
		xferfcn[-1] = xferfcn[-1].real
		return numpy.fft.inverse_real_fft( self.ss * xferfcn )


class gammatone_filterbank(object):
	def __init__(self, data, dt, Dt):
		self.dt = dt
		self.data = data

	def filter(self, fc):
		return gammatone.gammatone(self.data, self.dt, fc, gammatone.M_BASILAR)


def perceptual_spec(data, dt, Dt, bmin=CBmin, bmax=CBmax, db=BBSZ,
			do_mod=0, do_dissonance=False, PlompBouman=True,
			do_peakalign=False):
	"""This returns something roughly like the neural signals leaving the ear.
	It filters into 1-erb-wide bins, then takes the cube root of
	the amplitude.
	@return: (channel_info, data, time_offset), where
		- C{time_offset} is the time of the the first output datum
			relative to the time of the  first input sample.
		- C{channel_info}
		- C{data}
	"""
	do_mod = int(do_mod)
	Neural_Time_Resolution = max(Neural_Tick, dt)
	m = data.shape[0]
	assert m*dt > Dt, "Tiny amount of data: %d*%g=%.2gs < Dt=%2g" % (m, dt, m*dt, Dt)
	# ntau = int(round(m*dt/Dt))
	ntau = int(M.floor(m*dt/Dt))
	# fbank = fft_filterbank(data, dt, Dt)
	fbank = gammatone_filterbank(data, dt, Dt)
	nband0 = int(M.ceil((bmax-bmin)/db))
	nbands = nband0
	assert do_mod in [0,1,2], "Do_mod=%s" % str(do_mod)
	if do_mod:
		nbands += int(do_mod)
		tk = []
	if do_dissonance:
		nbands += 1
		diss = roughness_c()
	if do_peakalign:
		nbands += 1
		palign = peakalign_c()
	neural = numpy.zeros((nbands, ntau), numpy.float)
	bctrs = []
	t0x = []
	iband = 0
	b = bmin
	while b < bmax:
		# print 'iband=', iband, 'b=', b, 'nbands=', nbands
		fc = erb_scale.erb_to_f(b)
		filtered_sig = fbank.filter(fc)
		hair_cells = numpy.maximum(filtered_sig/threshold(fc), 0.0)**(2*E)
		# pylab.plot(hair_cells)
		# pylab.title('hair cells')
		# pylab.figure()
		pwrfilt, t0 = power.smooth(hair_cells, dt, Dt)
		# pylab.plot(pwrfilt)
		t0x.append(t0)
		if PlompBouman:
			pwrfilt = numpy.maximum(VM.lopass_first_order(pwrfilt, Dt/tau_lp(fc)), 0.0)
		else:
			pwrfilt = numpy.maximum(pwrfilt, 0.0)
		# pylab.plot(pwrfilt)
		# pylab.show()
		neural[iband,:] = pwrfilt[:ntau]
		bctrs.append({'type':'band', 'smooth': tau_lp(fc), 'fc': fc,
				'erb': b, 'E': E, 'id': 'B%.1f' % b
				})

		if do_mod or do_dissonance or do_peakalign:
			tkfilt, t0 = power.smooth(hair_cells, dt, Neural_Time_Resolution)
		if do_dissonance:
			diss_bw = min(DISS_BWF*erb_scale.ebw(b), MAX_DISS_FREQ)
			diss.add(tkfilt, Neural_Time_Resolution, diss_bw)
		if do_mod:
			tk.append(tkfilt)
		if do_peakalign:
			palign.add(tkfilt, Neural_Time_Resolution, fc)
		b += db
		iband += 1
	assert iband == nband0

	if do_mod == 1:
		tksum, tkn, tkmin = process_voicing(tk, Neural_Time_Resolution, Dt)
		neural[iband,:] = (tksum/tkn-tkmin)[:ntau]*0.15
		bctrs.append({'type':'haspitch', 'id':'haspitch1', 'variant': 1,
				'Fentropy': -M.log(len(tk))
				})
		iband += 1
		assert len(bctrs) == iband
	elif do_mod == 2:
		Voicing_divide = 0.5*(CBmax+CBmin)
		tk_low = []
		tk_high = []
		for (bctr, tki) in zip(bctrs, tk):
			assert tki.shape[0] > 0
			if bctr['erb'] > Voicing_divide:
				tk_high.append(tki)
			else:
				tk_low.append(tki)
		tksum_low, tkn_low, tkmin_low = process_voicing(tk_low, Neural_Time_Resolution, Dt)
		tksum_high, tkn_high, tkmin_high = process_voicing(tk_high, Neural_Time_Resolution, Dt)
		avgmmin = (tksum_low+tksum_high)/(tkn_low+tkn_high) - numpy.minimum(tkmin_low, tkmin_high)
		neural[iband,:] = avgmmin[:ntau]*0.15
		bctrs.append({'type':'haspitch', 'id':'haspitch_all',
				'variant': 'all',
				'Fentropy': -M.log(len(tk))
				})
		iband += 1

		neural[iband,:] = (tksum_high/tkn_high-tkmin_high)[:ntau]*0.15
		bctrs.append({'type':'haspitch', 'id':'haspitch_high',
				'variant': 'high',
				'Fentropy': -M.log(len(tk_high))
				})
		iband += 1
		assert len(bctrs) == iband
	if do_dissonance:
		neural[iband,:] = diss.get(Dt)[:ntau]*20.0
		# pylab.plot(diss.get(Dt))
		# pylab.title('roughness_c')
		# pylab.show()
		bctrs.append({'type':'roughness', 'id':'roughness1',
				'variant': 1,
				'Fentropy': -M.log(diss.n)
				})
		iband += 1
	if do_peakalign:
		neural[iband,:] = palign.get(Dt)[:ntau]
		bctrs.append({'type':'peakalign', 'id':'peakalign1',
				'variant': 1,
				'Fentropy': -M.log(palign.n)
				})
		iband += 1
	assert iband == neural.shape[0], "iband=%d != shape=%s" % (iband, str(neural.shape))

	return (bctrs, neural, gpkmisc.median(t0x))



def test():
	dt = 1e-4
	d = numpy.zeros((10000,1))
	for i in range(0, 10000, 100):
		d[i,0] = 1.0
	return gpkimgclass.gpk_img({'CDELT2': dt}, d)



__version__ = "$Revision: 1.43 $"
__date__ = "$Date: 2007/03/07 23:54:40 $"


if __name__ == '__main__':
	# try:
		# import psyco
		# psyco.full()
	# except ImportError:
		# pass
	import gpkimgclass
	DT = 0.01	# Seconds.  Default output sampling interval.
	arglist = sys.argv[1:]
	Blocksize = 10.0
	arglist0 = arglist
	column = None
	signal = None
	outfile = "-"
	extrahdr = {}
	while arglist and arglist[0].startswith('-'):
		arg = arglist.pop(0)
		if arg == '--':
			break
		elif arg == '-dt':
			DT = float(arglist.pop(0))
		elif arg == '-f':
			signal = gpkimgclass.read(arglist.pop(0))
		elif arg == '-c':
			tmp = arglist.pop(0)
			try:
				column = int( tmp )
			except ValueError:
				column = tmp
		elif arg == '-b':
			Blocksize = float(arglist.pop(0))
		elif arg == '-plot':
			import pylab
		elif arg == '-test':
			signal = test()
			column = 0
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
	if arglist:
		if signal is None:
			signal = gpkimgclass.read(arglist[0])
		else:
			die.die("Usage: cannot specify name both with -f and as last argument.")

	if signal is None:
		die.info("No signal file specified.")
		print __doc__
		die.exit(1)
	try:
		signal.column(column)
	except KeyError:
		die.info("File has %d columns" % signal.n[1])
		die.die("Bad column: %s" % str(column))

	bctrs, neural, tshift = block_percep_spec(signal.column(0), signal.dt(), DT,
					do_mod=True, do_dissonance=True,
					do_peakalign=True,
					blocksize=Blocksize)
	o = numpy.transpose(neural)
	if pylab:
		pylab.matshow(numpy.transpose(o))
		pylab.show()

	hdr = signal.hdr.copy()
	hdr['program'] = sys.argv[0]
	hdr['ARGV'] = arglist0
	hdr['input_file'] = signalfile
	hdr['column'] = column
	hdr['CDELT2'] = DT
	hdr['CRPIX2'] = 1
	hdr['CRVAL2'] = signal.start() + tshift
	hdr['CRPIX1'] = 1
	hdr['CRVAL1'] = bctrs[0]['erb']
	hdr['CDELT1'] = bctrs[1]['erb']-bctrs[0]['erb']
	hdr['BITPIX'] = -32
	hdr.update( extrahdr )
	for (i,b) in enumerate(bctrs):
		hdr['TTYPE%d' % i] = b['id']
	gpkimgclass.gpk_img(hdr, o).write(outfile)
