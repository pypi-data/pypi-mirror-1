#!/usr/bin/env python


from gmisclib import erb_scale
from gmisclib import Num
from gpk_voicing import percep_spec
from gpk_voicing import fv_misc as M
SillyWidthException = M.SillyWidthException


def feature_vec(data, dt, DT,
		LF=1.0, Nsv=M.NSV, ELF=None,
		do_voicing=1, do_dissonance=False, PlompBouman=True):
	FORMANT_LOW = erb_scale.f_to_erb(200.0)
	FORMANT_HIGH = erb_scale.f_to_erb(4000.0)
	assert DT > 0.0 and float(DT)>0.0
	assert LF > 0.0 and float(LF)>0.0
	bmin = erb_scale.f_to_erb(100.0)
	bmax = erb_scale.f_to_erb(6000.0)
	all_ectrs, all_ps, t0 = percep_spec.perceptual_spec(data, dt, DT,
							bmin, bmax, M.DB,
							do_mod=do_voicing,
							do_dissonance=False,
							PlompBouman=PlompBouman
							)

	band_indices = [i for (i,ec) in enumerate(all_ectrs) if ec['type']=='band']
	# print 'band_indices=', band_indices
	neural = all_ps.take(band_indices, axis=0)
	ectrs = [ec for ec in all_ectrs if ec['type']=='band']
	# print 'ectrs=', ectrs
	nband_indices = [i for (i,ec) in enumerate(all_ectrs) if ec['type']!='band']
	# print 'nband_indices=', nband_indices
	nneural = all_ps.take(nband_indices, axis=0)
	nectrs = [ec for ec in all_ectrs if ec['type']!='band']
	# print 'nectrs=', nectrs

	assert nneural.shape[1]==neural.shape[1]
	assert neural.shape[1]==all_ps.shape[1]
	assert neural.shape[0]+nneural.shape[0] == all_ps.shape[0]

	neural_now = Num.average(neural, axis=0)
	# pylab.plot(neural_now)
	# pylab.title('neural_now')
	# pylab.show()
	assert neural_now.shape[0] == neural.shape[1]
	neural_avg = Num.sum(neural_now**2)/Num.sum(neural_now)
	# print 'neural_avg=', neural_avg
	Num.divide(neural, neural_avg, neural)
	Num.divide(neural_now, neural_avg, neural_now)
	# pylab.plot(neural_now)
	# pylab.title('normed neural_now')
	# pylab.show()

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
	Vl = 0.06
	w = int(round(Vl*LF/DT))
	tmpo, tmpd = M.vowel(w, ectrs, neural, neural_now, Nsv,
						formant_low=FORMANT_LOW,
						formant_high=FORMANT_HIGH
						)
	o.extend(tmpo)
	descr.extend(tmpd)
	assert len(descr)==len(o), "Descriptor mismatch"

	if do_dissonance:
		raise RuntimeError, "Assumes dissonance=False"

	if do_voicing:
		Hpl = 0.07
		w = int(round(Hpl*LF/DT))
		tmpo, tmpd = M.haspitch(w, nectrs, nneural, neural_now, Nsv)
		o.extend(tmpo)
		descr.extend(tmpd)

	assert len(descr)==len(o), "Descriptor mismatch"
	N = neural[0].shape[0]
	for (i, (tmp, dsc)) in enumerate(zip(o, descr)):
		assert tmp.shape == (N,), "Wrong size: %d, %s = %d vs. %d" % (i, str(dsc), tmp.shape[0], N)

	return (o, descr, DT, t0)
