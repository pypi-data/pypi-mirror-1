#!/usr/bin/env python


from gmisclib import erb_scale
from gmisclib import Num
from gpk_voicing import percep_spec
from gpk_voicing import fv_misc as M
SillyWidthException = M.SillyWidthException


def feature_vec(data, dt, DT,
		LF=1.0, Nsv=M.NSV,
		ELF=1.0,
		do_voicing=1, do_dissonance=True):
	FORMANT_LOW = erb_scale.f_to_erb(60.0)
	FORMANT_HIGH = erb_scale.f_to_erb(5000.0)
	assert DT > 0.0 and float(DT)>0.0
	assert LF > 0.0 and float(LF)>0.0
	bmin = erb_scale.f_to_erb(80.0)
	bmax = erb_scale.f_to_erb(7000.0)
	all_ectrs, all_ps, t0 = percep_spec.perceptual_spec(data, dt, DT,
							bmin, bmax, M.DB,
							do_mod=do_voicing,
							do_dissonance=do_dissonance,
							PlompBouman=True
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

	neural_now = Num.average(neural, axis=0)	# Average over frequency.
	assert neural_now.shape[0] == neural.shape[1]
	neural_avg = Num.sum(neural_now**2)/Num.sum(neural_now)	# Average over time.
		# neural_avg is a scalar, grand average.
	Num.divide(neural, neural_avg, neural)
		# Now, we've normalized by an over-all average loudness.
	Num.divide(neural_now, neural_avg, neural_now)
		# Now, we've normalized by an over-all average loudness.

	assert nneural.shape[0] < nneural.shape[1]
	assert len(nectrs) == nneural.shape[0]
	for (i,e) in enumerate(nectrs):
		if e['type'] == 'haspitch':
			Num.divide(nneural[i,:], neural_avg, nneural[i,:])
		if e['type'] == 'dissonance':
			Num.divide(nneural[i,:], neural_avg, nneural[i,:])

	# print '# neural_avg=', neural_avg
	o = []
	descr = []
	wset = set([0])
	for vl in [0.04]:
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

	wset = set([0])
	for fel in [0.06]:
		w = int(round(fel*ELF/DT))
		if not w in wset:
			tmpo, tmpd = M.fricative_edge(w, ectrs, neural, neural_now, Nsv,
						do_abs=False
						)
			o.extend(tmpo)
			descr.extend(tmpd)
			wset.add(w)

	wset = set([0])
	for sel in [0.04]:
		w = int(round(sel*LF/DT))
		if not w in wset:
			tmpo, tmpd = M.spectral_entropy(w, ectrs, neural, neural_now, Nsv)
			o.extend(tmpo)
			descr.extend(tmpd)
			wset.add(w)
		assert len(descr)==len(o), "Descriptor mismatch"


	if do_voicing:
		wset = set([0])
		for hpl in [0.05]:
			w = int(round(hpl*LF/DT))
			if not w in wset:
				tmpo, tmpd = M.haspitch(w, nectrs, nneural, neural_now, Nsv)
				o.extend(tmpo)
				descr.extend(tmpd)
				wset.add(w)
	if do_dissonance:
		wset = set([0])
		for dsl in [0.05]:
			w = int(round(dsl*LF/DT))
			if not w in wset:
				tmpo, tmpd = M.dissonance(w, nectrs, nneural, neural_now, Nsv)
				o.extend(tmpo)
				descr.extend(tmpd)
				wset.add(w)

	assert len(descr)==len(o), "Descriptor mismatch"
	N = neural[0].shape[0]
	for (i, (tmp, dsc)) in enumerate(zip(o, descr)):
		assert tmp.shape == (N,), "Wrong size: %d, %s = %d vs. %d" % (i, str(dsc), tmp.shape[0], N)

	return (o, descr, DT, t0)

