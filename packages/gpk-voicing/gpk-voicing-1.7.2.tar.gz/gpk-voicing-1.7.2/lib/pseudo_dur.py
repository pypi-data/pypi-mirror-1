#!/usr/bin/env python

"""Duration estimator for speech.

Usage: s_slope [flags]
Flags: -f FFF opens file FFF for reading.
	-c XXX  selects column XXX (either a data name or an integer).
	-o FFF  sets the output file.
	-dt #.##   Sets the interval for calculating the output.

It takes a local spectrum,
bins it onto the Bark scale,
converts to perceptual loudness (via **E).
Then, it computes a measure of how far you can go
from each point before the spectrum changes too much.
"""

import math as M
import numpy


def pdur_guts(s, t, dir, Dt, C):
	"""t is an integer; an index into the data.
	S is the normalized perceptual spectrum."""
	n = len(s)
	assert s.shape[1] < 200, "Implausibly long feature vector.  Is s transposed?"
	sumdiff = 0.0
	len_sum = 0.5	# The integral for the i==t case is trivial.
	ctr_sum = 0.125*dir	# The integral for i==t is trivial.
	i = t + dir
	while i>=0 and i<n and sumdiff<8:
		delta_diff = Dt * C * numpy.sum( numpy.absolute(s[i]-s[t])**2 )

		# We assume that the spectrum is s[i] in the
		# region from i-0.5 to i+0.5, and compute the
		# integral( M.exp(-integral((s(t0)-s(t''))**2 from 0 to t', dt''))
		# 	from 0 to i+0.5, dt')
		# The constancy of s over the interval (i-0.5,i+0.5)
		# makes the inner integral piecewise linear.
		# Sumdiff holds integral((s(t0)-s(t''))**2 from 0 to i-0.5)
		if delta_diff <= 0:
			# assume delta_diff = 0
			lsd = M.exp(-sumdiff)
			len_sum += lsd
			# integral( (t''-t0)*M.exp(-integral((s(t0)-s(t''))**2 from 0 to t', dt''))
			# 	from 0 to i+0.5, dt')
			slopeint = M.exp(-sumdiff) * 0.5
			ctr_sum += (i-t-0.5*dir)*lsd + dir * slopeint
			i += dir
		else:
			lsd = M.exp(-sumdiff) * (1.0-M.exp(-delta_diff))/delta_diff
			len_sum += lsd
			# integral( (t''-t0)*M.exp(-integral((s(t0)-s(t''))**2 from 0 to t', dt''))
			# 	from 0 to i+0.5, dt')
			slopeint = M.exp(-sumdiff)	\
					* (1.0-M.exp(-delta_diff)*(1+delta_diff))/delta_diff**2
			ctr_sum += (i-t-0.5*dir)*lsd + dir * slopeint
			i += dir
			sumdiff += delta_diff
		# Now, sumdiff holds integral((s(t0)-s(t''))**2 from 0 to i+0.5)
	# print 't=', t, sum
	return (len_sum*Dt, ctr_sum*Dt)


