import math
import cython
import numpy
cimport numpy
from cython import wraparound

from gmisclib import hilbert_xform

ctypedef numpy.float_t DTYPE

cdef extern from "math.h":
	double floor(double)
	double ceil(double)
	double cos(double)

cdef extern from "gpklib.h":
	int roundI(double)



cdef int max(int a, int b):
	if a > b:
		return a
	return b

cdef int min(int a, int b):
	if a < b:
		return a
	return b


@cython.boundscheck(False)
def smooth_guts(numpy.ndarray[DTYPE, ndim=1, mode="c"] ph,
		double dt_in, double dt_out, double w, wt=None):
	assert w >= 1.0
	assert dt_in <= dt_out
	cdef double dt_ratio = dt_out/dt_in
	cdef int no = <int>(floor(ph.shape[0]/dt_ratio))
	cdef numpy.ndarray[DTYPE, ndim=1, mode="c"] o = numpy.zeros((no,))
	cdef numpy.ndarray[DTYPE, ndim=1, mode="c"] owt, iwt, window
	if wt is not None:
		owt = numpy.zeros((no,), numpy.float)
		iwt = numpy.as_array(wt)

	cache = {}

	cdef double SS = float(10.0)
	cdef int ni = ph.shape[0]
	cdef int i, j0, je, j
	cdef double jr, jrr, s, sw, wtmp
	for i in range(no):
		jr = i*dt_ratio
		jrr = roundI(jr*SS)/SS
		j0 = max(0, <int>(ceil(jrr-w)))
		je = min(ni, <int>(floor(jrr+w))+1)
		assert je > j0
		wkey = (je-j0, jrr-j0)
		try:
			window = cache[wkey]
		except KeyError:
			window = _wfunc(je-j0, jrr-j0, w)
			cache[wkey] = window

		s = 0.0
		sw = 0.0
		if wt is not None:
			for j in range(je-j0):
				wtmp = iwt[j0+j]*window[j]
				sw += wtmp
				s += wtmp * ph[j0+j]
		else:
			for j in range(je-j0):
				s += ph[j0+j]*window[j]
				sw += window[j]
		o[i] = s/sw
	if wt is None:
		return o, None
	return o, owt



@cython.boundscheck(False)
def _wfunc(int n, double ctr, double w):
	cdef int i
	cdef double phase
	cdef double piw = math.pi/w
	cdef numpy.ndarray[DTYPE, ndim=1, mode="c"] o = numpy.zeros((n,))
	for i in range(n):
		phase = piw*(i-ctr)
		assert phase>=-3.142 and phase<=3.142, "Bad phases: %s or %s for %s %s %s" % (str(phase), str(phase), str(n), str(ctr), str(w))
		o[i] = 1.0 + cos(phase)
	return o

