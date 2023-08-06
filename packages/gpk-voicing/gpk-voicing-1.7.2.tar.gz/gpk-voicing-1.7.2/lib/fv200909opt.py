#!/usr/bin/env python

"""Feature vectors for optimized DTW alignment.
Exemplar project with Ladan Baghai-Ravary.
"""

import math
from gmisclib import erb_scale
from gmisclib import Num
from gpk_voicing import percep_spec
from gpk_voicing import fv_misc as M
SillyWidthException = M.SillyWidthException

DB = 0.85

def irx(a):
	return max(1, int(round(a)))

def feature_vec(data, dt, DT,
		LF=1.0, Nsv=M.NSV, ELF=1.0,
		do_voicing=1, do_dissonance=False,
		PlompBouman=False, do_pdur=False):
	assert not do_pdur and not do_dissonance
	FORMANT_LOW = erb_scale.f_to_erb(120.0)
	FORMANT_HIGH = erb_scale.f_to_erb(6000.0)
	assert DT > 0.0 and float(DT)>0.0
	assert LF > 0.0 and float(LF)>0.0
	bmin = erb_scale.f_to_erb(80.0)
	bmax = erb_scale.f_to_erb(6000.0)
	ectrs, neural, t0 = percep_spec.perceptual_spec(data, dt, DT,
							bmin, bmax, DB,
							do_mod=do_voicing,
							do_dissonance=do_dissonance,
							do_peakalign=True,
							PlompBouman=PlompBouman
							)

	band_indices = [i for (i,ec) in enumerate(ectrs) if ec['type']=='band']
	neural_b = neural.take(band_indices, axis=0)
	assert neural.shape[1]==neural.shape[1]

	neural_now = Num.average(neural_b, axis=0)	# Average over frequency.
	assert neural_now.shape[0] == neural.shape[1]
	neural_avg = Num.sum(neural_now**2)/Num.sum(neural_now)	# Average over time.
		# neural_avg is a scalar, grand average.
	Num.divide(neural, neural_avg, neural)
		# Now, we've normalized by an over-all average loudness.
	Num.divide(neural_now, neural_avg, neural_now)
		# Now, we've normalized by an over-all average loudness.

	assert neural_b.shape[0] <= neural.shape[1]
	for (i,e) in enumerate(ectrs):
		if e['type'] == 'haspitch':
			Num.divide(neural[i,:], neural_avg, neural[i,:])
		if e['type'] == 'dissonance':
			Num.divide(neural[i,:], neural_avg, neural[i,:])
		if e['type'] == 'peakalign':
			Num.divide(neural[i,:], neural_avg**2, neural[i,:])

	# print '# neural_avg=', neural_avg
	o = []
	descr = []
	w = irx(0.04*LF/DT)
	tmpo, tmpd = M.vowel(w, ectrs, neural, neural_now, Nsv,
						formant_low=FORMANT_LOW,
						formant_high=FORMANT_HIGH
						)
	o.extend(tmpo)
	descr.extend(tmpd)
	assert len(descr)==len(o), "Descriptor mismatch"

	w = irx(0.04*ELF/DT)
	tmpo, tmpd = M.fricative_edge(w, ectrs, neural, neural_now, Nsv,
						do_abs=False
						)
	o.extend(tmpo)
	descr.extend(tmpd)
	assert len(descr)==len(o), "Descriptor mismatch"

	if do_voicing:
		w = irx(0.02*math.sqrt(LF)/DT)
		tmpo, tmpd = M.haspitch(w, ectrs, neural, neural_now, Nsv)
		o.extend(tmpo)
		descr.extend(tmpd)
	assert len(descr)==len(o), "Descriptor mismatch"

	w = irx(0.03*ELF/DT)
	tmpo, tmpd = M.peakiness(w, ectrs, neural, neural_now, Nsv)
	o.extend(tmpo)
	descr.extend(tmpd)
	assert len(descr)==len(o), "Descriptor mismatch"

	N = neural[0].shape[0]
	for (i, (tmp, dsc)) in enumerate(zip(o, descr)):
		assert tmp.shape == (N,), "Wrong size: %d, %s = %d vs. %d" % (i, str(dsc), tmp.shape[0], N)

	return (o, descr, DT, t0)

