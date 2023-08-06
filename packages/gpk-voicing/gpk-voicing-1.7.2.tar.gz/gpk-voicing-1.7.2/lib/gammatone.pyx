#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#============================================================
#GAMMATONE_C: A C implementation of the 4th order gammatone filter
#-------------------------------
#  [bm, env, instp, ] = gammatone_c(x, fs, cf, hrect) 
#
#  x     - input signal
#  fs    - sampling frequency (Hz)
#  cf    - centre frequency of the filter (Hz)
#  hrect - half-wave rectifying if hrect = 1 (default 0)
#
#
#  bm    - basilar membrane displacement
#  env   - instantaneous envelope
#  instp - instantaneous phase (unwrapped radian)
#
#  >> mex gammatone_c.c
#  >> bm = gammatone_c(x, 16000, 200);
#
# This was translated from MATLAB to python by Greg Kochanski.
# More detail on the original can be found at:
#  http://www.dcs.shef.ac.uk/~ning/resources/gammatone/
# Original author:
#  Ning Ma, University of Sheffield
#  n.ma@dcs.shef.ac.uk, 09 Mar 2006
# 

import math
import cython
import numpy
cimport numpy
ctypedef numpy.float_t DTYPE

cdef extern from "math.h":
	double floor(double)
	double exp(double)
	double sqrt(double)
	double sin(double x)
	double cos(double x)
	double fabs(double x)
	double atan2(double y, double x)

# /*=======================
 # * Useful Const
 # *=======================
cdef double BW_CORRECTION = 1.0190
cdef double M_PI = math.pi

# /*=======================
 # * Utility functions
 # *=======================

cdef double myMod(double x, double y):
	return x - y*floor(x/y)

cdef double erb(double x):
	return 24.7*(4.37e-3*x+1.0)

M_BASILAR = 0
M_BASILAR_RECT = 1
M_AMP_PHASE = 2

#  [bm, env, instp, ] = gammatone_c(x, fs, cf, hrect) 
@cython.boundscheck(False)
def gammatone(numpy.ndarray[DTYPE, ndim=1, mode="c"] x, double dt, double cf, int mode):
	assert mode in [M_BASILAR, M_BASILAR_RECT, M_AMP_PHASE]
	cdef int hmode = mode
	cdef int nsamples = x.shape[0]
#/*=========================================
# * output arguments
# *=========================================
	cdef numpy.ndarray[DTYPE, ndim=1, mode="c"] bm
	cdef numpy.ndarray[DTYPE, ndim=2, mode="c"] env_phase
	if hmode==0 or hmode==1:
		bm = numpy.zeros((nsamples,))
	else:
		env_phase = numpy.zeros((nsamples,2))

#/*=========================================
# * Initialising variables
# *=========================================
	cdef double oldphase = 0.0
	cdef double tpt = ( M_PI + M_PI ) * dt
	cdef double tptbw = tpt * erb ( cf ) * BW_CORRECTION
	cdef double a = exp ( -tptbw )

#/* based on integral of impulse response */
	cdef double gain = ( tptbw*tptbw*tptbw*tptbw ) / 3.0

#/* Update filter coefficiants */
	cdef double a1 = 4.0*a
	cdef double a2 = -6.0*a*a
	cdef double a3 = 4.0*a*a*a
	cdef double a4 = -a*a*a*a
	cdef double a5 = 4.0*a*a
	cdef double p0r = 0.0
	cdef double p1r = 0.0
	cdef double p2r = 0.0
	cdef double p3r = 0.0
	cdef double p4r = 0.0
	cdef double p0i = 0.0
	cdef double p1i = 0.0
	cdef double p2i = 0.0
	cdef double p3i = 0.0
	cdef double p4i = 0.0
 
#/*===========================================================
# * exp(a+i*b) = exp(a)*(cos(b)+i*sin(b))
# * q = exp(-i*tpt*cf*t) = cos(tpt*cf*t) + i*(-sin(tpt*cf*t))
# * qcos = cos(tpt*cf*t)
# * qsin = -sin(tpt*cf*t)
# *===========================================================
	cdef double coscf = cos ( tpt * cf )
	cdef double sincf = sin ( tpt * cf )
	cdef double qcos = 1.0	#   /* t=0 & q = exp(-i*tpt*t*cf)*/
	cdef double qsin = 0.0
	cdef double oldcs, oldsn, dp, dps, u0r, u0i
	cdef int t
	for t in range(nsamples):
		#/* Filter part 1 & shift down to d.c. */
		p0r = qcos*x[t] + a1*p1r + a2*p2r + a3*p3r + a4*p4r
		p0i = qsin*x[t] + a1*p1i + a2*p2i + a3*p3i + a4*p4i

		#/* Filter part 2 */
		u0r = p0r + a1*p1r + a5*p2r
		u0i = p0i + a1*p1i + a5*p2i

		#/* Update filter results */
		p4r = p3r
		p3r = p2r
		p2r = p1r
		p1r = p0r
		p4i = p3i
		p3i = p2i
		p2i = p1i
		p1i = p0i
  
		#/*==========================================
		#* Basilar membrane response
		#* 1/ shift up in frequency first: (u0r+i*u0i) * exp(i*tpt*cf*t)
		#				= (u0r+i*u0i) * (qcos + i*(-qsin))
		#* 2/ take the real part only: bm = real(exp(j*wcf*kT).*u) * gain;
		#*==========================================
		if hmode==0 or hmode==1:
			bm[t] = ( u0r * qcos + u0i * qsin ) * gain
			if hmode==1 and bm[t] < 0:
				bm[t] = 0.0	#  /* half-wave rectifying */

		#/*==========================================
		#* Instantaneous Hilbert envelope
		#* env = abs(u) * gain;
		#*==========================================
		if hmode==2:
			env_phase[t,0] = sqrt ( u0r * u0r + u0i * u0i ) * gain

		#/*==========================================
		#* Instantaneous phase
		#* instp = unwrap(angle(u));
		#*==========================================
			env_phase[t,1] = atan2 ( u0i, u0r )
			# /* unwrap it */
			dp = env_phase[t,1] - oldphase
			if fabs ( dp ) > M_PI:
				dps = myMod ( dp + M_PI, 2 * M_PI) - M_PI;
				if dps == -M_PI and dp > 0:
					dps = M_PI
				env_phase[t,1] = env_phase[t,1] + dps - dp
			oldphase = env_phase[t,1];

		# /*====================================================
		# * The basic idea of saving computational load:
		# * cos(a+b) = cos(a)*cos(b) - sin(a)*sin(b)
		# * sin(a+b) = sin(a)*cos(b) + cos(a)*sin(b)
		# * qcos = cos(tpt*cf*t) = cos(tpt*cf + tpt*cf*(t-1))
		# * qsin = -sin(tpt*cf*t) = -sin(tpt*cf + tpt*cf*(t-1))
		# *====================================================
		oldcs = qcos
		oldsn = qsin
		qcos = coscf * oldcs + sincf * oldsn
		qsin = coscf * oldsn - sincf * oldcs

	if hmode==0 or hmode==1:
		return bm
	return env_phase





@cython.boundscheck(False)
def hipass_first_order(numpy.ndarray[DTYPE, ndim=1, mode="c"] d, double cutoff_freq):
	"""A first-order high-pass filter.
	Cutoff freq is measured in cycles per point."""

	assert cutoff_freq >= 0.0
	cdef int n = d.shape[0]
	cdef numpy.ndarray[DTYPE, ndim=1, mode="c"] o = numpy.zeros((n,))
	cdef double tau = 1.0/(2*M_PI*cutoff_freq)
	cdef double alpha = tau/(tau+1.0)
	cdef int i
	for i in range(1,n):
		o[i] = alpha * (o[i-1] + (d[i] - d[i-1]))
	return o


@cython.boundscheck(False)
def lopass_first_order(numpy.ndarray[DTYPE, ndim=1, mode="c"] d, cutoff_freq):
	"""A first-order low-pass filter.
	Cutoff freq is measured in cycles per point."""
	assert cutoff_freq >= 0.0
	cdef int n = d.shape[0]
	cdef numpy.ndarray[DTYPE, ndim=1, mode="c"] o = numpy.zeros((n,))
	cdef double tau = 1.0/(2*M_PI*cutoff_freq)
	cdef double alpha = 1.0/(tau+1.0)
	cdef int i
	for i in range(1,n):
		o[i] = o[i-1] + alpha * (d[i]-o[i-1])
	return o
