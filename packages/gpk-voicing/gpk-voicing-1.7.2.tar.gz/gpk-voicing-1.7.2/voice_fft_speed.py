#! python

"""A little program to check that voice_misc._fftwork() is correct."""


from gpk_voicing import voice_misc
import numpy
import pylab
import time


def plot(start, end):
	x = []
	y = []
	z = []
	ws = 0.0
	ts = 0.0
	for n in range(start, end):
		x.append(n)
		w = voice_misc._fftwork_real(n)
		# w = voice_misc._fftwork(n)
		y.append(w)
		q = numpy.zeros((n,))
		k = 0
		t0 = time.clock()
		while time.clock() < t0 + 0.1:
			# numpy.fft.fft(q)
			s = numpy.fft.rfft(q)
			numpy.fft.irfft(s)
			k += 1
		t1 = time.clock()
		dt = (t1-t0)/k
		z.append(dt)
		ts += dt
		ws += w
	wscaled = [w*(ts/ws) for w in y]
	pylab.plot(x, wscaled, 'g')
	pylab.plot(x, z, 'r+')
	pylab.show()


if __name__ == '__main__':
	plot(127, 257)
