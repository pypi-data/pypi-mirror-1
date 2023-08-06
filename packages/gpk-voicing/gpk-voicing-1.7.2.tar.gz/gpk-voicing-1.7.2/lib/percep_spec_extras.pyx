import cython
import numpy
cimport numpy
ctypedef numpy.float_t DTYPE

cdef extern from "math.h":
	double fabs(double x)



def list_accum_abs_sub_dly(tk, dly):
	cdef int lng = tk[0].shape[0]
	cdef int dlyn = dly//2
	cdef int dlyp = dly - dlyn
	cdef numpy.ndarray[DTYPE, ndim=1, mode="c"]o = numpy.zeros((lng,))
	cdef numpy.ndarray[DTYPE, ndim=1, mode="c"] tkd
	cdef double a, b
	cdef int i
	for tkd in tk:
		for i in range(dlyn,lng-dlyp):
			a = tkd[i+dlyp]
			b = tkd[i-dlyn]
			o[i] += fabs(a-b)
	return o

