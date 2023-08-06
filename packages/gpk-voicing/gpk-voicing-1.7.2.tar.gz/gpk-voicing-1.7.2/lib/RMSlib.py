import math
import numpy
from gpk_voicing import voice_misc
from gpk_voicing import power




def one_pk_pk(t, data, dt, Pkwdt):
	"""Measure the peak-to-peak amplitude near time t.
	@param t: the time to measure near (units of seconds)
	@type t: float (seconds).
	@param data: the time-series.
	@type data: numpy.ndarray
	@param dt: the sampling interval for data
	@type dt: float (seconds).
	@param Pkwdt: Half-width of region over which to compute
		the peak-to-peak amplitude.   The low end of the
		frequency response will be on the order of 1/Pkwdt.
	@type Pkwdt: float (seconds).
	@return: scalar peak-to-peak amplitude
	@rtype: float
	"""
	s, e = voice_misc.start_end(t, dt, int(round(Pkwdt/dt)), data.shape[0])
	d = data[s:e]
	return d[ numpy.argmax( d ) ] - d[ numpy.argmin(d) ]


def compute_intensity(data, dt, DT, DR, HPF, DTSmooth):
	"""Measure the time-series of RMS of a data array data.
	DT is the sampling interval for the resulting RMS time series."""
	if HPF is not None:
		data = voice_misc.hipass_sym_butterworth(data, HPF*dt)
	if DR == 'rms':
		pwr, t0 = power.smooth(data**2, dt, DT, DTSmooth)
		rms = numpy.sqrt(pwr)
	elif DR == 'avd':
		rms,t0 = power.smooth(numpy.absolute(data), dt, DT, DTSmooth)
	elif DR == 'pkpk':
		ns = int(math.floor(data.shape[0]*(dt/DT)))
		# print 'ns=', dt, data.shape[0], DT, dt*data.shape[0]/DT
		pkpk = numpy.zeros((ns,))
		for t in range(ns):
			pkpk[t] = one_pk_pk(t*DT, data, dt, math.hypot(DTSmooth, DT))
		rms,t0 = power.smooth(pkpk, DT, DT, DTSmooth)
	else:
		raise ValueError, 'Bad DR=%s' % DR
	return (rms,t0)


