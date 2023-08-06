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

from gmisclib import Num
from gmisclib import erb_scale

from gpk_voicing import percep_spec as PS
from gpk_voicing import fv_misc as FVM

def feature_vec(data, dt, Dt,
		Nsv=FVM.NSV
		):
	FORMANT_LOW = erb_scale.f_to_erb(200.0)
	FORMANT_HIGH = erb_scale.f_to_erb(4000.0)
	assert Dt > 0.0 and float(Dt)>0.0
	bmin = erb_scale.f_to_erb(100.0)
	bmax = erb_scale.f_to_erb(6000.0)
	# all_ectrs, all_ps, t0 = PS.perceptual_spec(data, dt, Dt, ...
	all_ectrs, all_ps, t0 = PS.block_percep_spec(data, dt, Dt,
							bmin=bmin, bmax=bmax, db=FVM.DB,
							do_mod=0,
							do_dissonance=False,
							PlompBouman=False
							)

	band_indices = [i for (i,ec) in enumerate(all_ectrs) if ec['type']=='band']
	neural = all_ps.take(band_indices, axis=0)
	ectrs = [ec for ec in all_ectrs if ec['type']=='band']
	nband_indices = [i for (i,ec) in enumerate(all_ectrs) if ec['type']!='band']
	nneural = all_ps.take(nband_indices, axis=0)
	nectrs = [ec for ec in all_ectrs if ec['type']!='band']

	assert nneural.shape[1]==neural.shape[1]
	assert neural.shape[1]==all_ps.shape[1]
	assert neural.shape[0]+nneural.shape[0] == all_ps.shape[0]
	assert len(data.shape) == 1
	assert abs(all_ps.shape[1]*Dt-data.shape[0]*dt) < 0.1*data.shape[0]*dt

	neural_now = Num.average(neural, axis=0)
	assert neural_now.shape[0] == neural.shape[1]
	neural_avg = Num.sum(neural_now**2)/Num.sum(neural_now)
	Num.divide(neural, neural_avg, neural)
	Num.divide(neural_now, neural_avg, neural_now)

	assert nneural.shape[0] < nneural.shape[1]
	assert len(nectrs) == nneural.shape[0]
	for (i,e) in enumerate(nectrs):
		assert e['type'] == 'band'

	# print '# neural_avg=', neural_avg
	Vl = 0.04
	w = int(round(Vl/Dt))
	o, descr = FVM.vowel(w, ectrs, neural, neural_now, Nsv,
						formant_low=FORMANT_LOW,
						formant_high=FORMANT_HIGH
						)
	assert len(descr)==len(o), "Descriptor mismatch"
	return (o, descr, t0)

