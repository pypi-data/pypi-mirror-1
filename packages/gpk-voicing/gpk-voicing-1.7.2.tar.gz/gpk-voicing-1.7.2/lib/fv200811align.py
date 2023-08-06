#!/usr/bin/env python


from gmisclib import erb_scale
from gmisclib import Num
from gpk_voicing import percep_spec
from gpk_voicing import fv_misc as M
SillyWidthException = M.SillyWidthException


def feature_vec(data, dt, DT,
		LF=1.0, Nsv=M.NSV, ELF=1.0,
		do_voicing=1, do_dissonance=True,
		PlompBouman=False, do_pdur=True):
	FORMANT_LOW = erb_scale.f_to_erb(200.0)
	FORMANT_HIGH = erb_scale.f_to_erb(4000.0)
	assert DT > 0.0 and float(DT)>0.0
	assert LF > 0.0 and float(LF)>0.0
	bmin = erb_scale.f_to_erb(80.0)
	bmax = erb_scale.f_to_erb(6000.0)
	ectrs, neural, t0 = percep_spec.perceptual_spec(data, dt, DT,
							bmin, bmax, M.DB,
							do_mod=do_voicing,
							do_dissonance=do_dissonance,
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

	# print '# neural_avg=', neural_avg
	o = []
	descr = []
	wset = set()
	for vl in [0.06]:
		# print 'vl=', vl, type(vl), 'LF=', LF, type(LF), 'DT=', DT, type(DT)
		w = int(round(vl*LF/DT))
		if not w in wset:
			tmpo, tmpd = M.vowel(w, ectrs, neural, neural_now, Nsv,
						formant_low=FORMANT_LOW,
						formant_high=FORMANT_HIGH
						)
			o.extend(tmpo)
			descr.extend(tmpd)
			wset.add(w)
	assert len(descr)==len(o), "Descriptor mismatch"

	wset = set()
	for fl in [0.02]:
		w = int(round(fl*ELF/DT))
		if not w in wset:
			tmpo, tmpd = M.fricative(w, ectrs, neural, neural_now, Nsv)
			o.extend(tmpo)
			descr.extend(tmpd)
			wset.add(w)
	assert len(descr)==len(o), "Descriptor mismatch"

	wset = set()
	for fel in [0.04]:
		w = int(round(fel*ELF/DT))
		if not w in wset:
			tmpo, tmpd = M.fricative_edge(w, ectrs, neural, neural_now, Nsv,
						do_abs=False
						)
			o.extend(tmpo)
			descr.extend(tmpd)
			wset.add(w)
	assert len(descr)==len(o), "Descriptor mismatch"

	wset = set()
	for sel in [0.03]:
		w = int(round(sel*LF/DT))
		if not w in wset:
			tmpo, tmpd = M.spectral_entropy(w, ectrs, neural, neural_now, Nsv)
			o.extend(tmpo)
			descr.extend(tmpd)
			wset.add(w)
		assert len(descr)==len(o), "Descriptor mismatch"
	assert len(descr)==len(o), "Descriptor mismatch"


	if do_voicing:
		wset = set()
		for hpl in [0.02]:
			w = int(round(hpl*LF/DT))
			if not w in wset:
				tmpo, tmpd = M.haspitch(w, ectrs, neural, neural_now, Nsv)
				o.extend(tmpo)
				descr.extend(tmpd)
				wset.add(w)
	assert len(descr)==len(o), "Descriptor mismatch"
	if do_dissonance:
		wset = set()
		for dsl in [0.06]:
			w = int(round(dsl*LF/DT))
			if not w in wset:
				tmpo, tmpd = M.dissonance(w, ectrs, neural, neural_now, Nsv)
				o.extend(tmpo)
				descr.extend(tmpd)
				wset.add(w)

	assert len(descr)==len(o), "Descriptor mismatch"
	if do_pdur:
		tmpo, tmpd = M.pdur(ectrs, neural, neural_now, DT)
		o.extend(tmpo)
		descr.extend(tmpd)

	assert len(descr)==len(o), "Descriptor mismatch"
	N = neural[0].shape[0]
	for (i, (tmp, dsc)) in enumerate(zip(o, descr)):
		assert tmp.shape == (N,), "Wrong size: %d, %s = %d vs. %d" % (i, str(dsc), tmp.shape[0], N)

	return (o, descr, DT, t0)

