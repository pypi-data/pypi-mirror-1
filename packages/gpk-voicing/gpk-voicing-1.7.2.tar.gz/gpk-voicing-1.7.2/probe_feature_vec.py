#!/usr/bin/env python


import os
import sys
import math
import random
from gmisclib import Num
from gmisclib import chunkio
from gmisclib import erb_scale
from gmisclib import gpkmisc
from gmisclib import g_pylab as pylab
from gmisclib import die
# import g_threading as GT

# THIS NEEDS TO BE FIXED. CODE WAS MOVED to lib.
from gpk_voicing import feature_vec as FV

DT = 0.005
XFORM = 'xform.chunk'


def get_fv(data, dt, bandonly=False, LengthFac=None, Nsv=None, SpecExp=None,
		DT=DT, simple=False):
	fvf = [FV.feature_vec, FV.simple_feature_vec][simple]
	o, descr, DT, t0 = fvf(data, dt,
					LF=LengthFac, Nsv=Nsv, SpecExp=SpecExp,
					DT=DT)
	print 'pfv: get_fv: DT=', DT
	if bandonly:
		for (i,dtmp) in enumerate(descr):
			if dtmp['type'] == 'haspitch':
				o[i] = Num.zeros(o[i].shape, Num.Float)
	o = Num.transpose(o)
	if XFORM:
		fac = chunkio.datachunk(open(XFORM, 'r')).read_NumArray()
		o = Num.matrixmultiply(o, fac)
	return (o, DT)


def window(t, dur):
	return Num.exp(t**2 * (-0.5/dur**2))


def get_response(erb, dur, ebw, bandonly=True,
			LengthFac=None, SpecExp=None, Nsv=None,
			DT=DT, simple=False):
	Q = 1.21
	dt = 1.0/24000.0
	Ne1 = int(round(0.15/dt))
	Ne2 = int(round(0.15/dt))
	tc = Ne1*dt + 3.0*dur
	Nd = Ne1 + int(round(6*dur/dt)) + Ne2
	sum = None
	M = int(math.ceil( 1.0/(erb_scale.ebw(erb)*dur) ))
	for i in range(M):
		ee = erb + (i-0.5*(M-1))/float(M)
		print 'i=', i, ee
		f = erb_scale.erb_to_f(ee)
		t = Num.arrayrange(Nd)*dt
		phi = t*(2*math.pi*f)
		a = math.cos(Q*i)
		b = math.sin(Q*i)
		d = (a*Num.cos(phi) + b*Num.sin(phi)) * window(t-tc, dur) * erb_scale.ebw(ee)
		# pylab.figure()
		# pylab.title('erb=%.2f i=%d f=%.1f' % (erb, i, f))
		# # pylab.plot(t, d)
		# # pylab.figure()
		o, Dt = get_fv(d, dt, bandonly=bandonly,
				LengthFac=LengthFac, SpecExp=SpecExp, Nsv=Nsv,
				DT=DT, simple=simple)
		# pylab.xlabel('time')
		# pylab.ylabel('feature number')
		# absmax = gpkmisc.N_maximum(Num.absolute(Num.ravel(o)))
		# pylab.imshow(Num.transpose(o), interpolation='nearest', vmax=absmax, vmin=-absmax)
		# # pylab.show()
		print 'DT=', Dt
		assert Dt == DT
		if sum is None:
			sum = o
		else:
			Num.add(sum, o, sum)
	return o/M



def erb_search(erbs, e):
	ebelow = min(erbs)-1
	eabove = max(erbs)+1
	ibelow = None
	iabove = None
	for (i,et) in enumerate(erbs):
		if et<e and et>ebelow:
			ebelow = et
			ibelow = i
		if et>e and et<eabove:
			eabove = et
			iabove = i
	if ibelow is not None and iabove is not None:
		return ibelow + (e-ebelow)*float(iabove-ibelow)/(eabove-ebelow)
	return None



def freq_grid(erbs):
	LFh = [500.0, 1500.0, 2500.0, 3500.0, 4500.0, 5500.0]
	LF = [1000.0, 2000.0, 3000.0, 4000.0, 5000.0, 6000.0]
	for lf in LFh:
		etmp = erb_search(erbs, erb_scale.f_to_erb(lf))
		if etmp is not None:
			pylab.axhline(etmp, color='k', linewidth=1)
	for lf in LF:
		etmp = erb_search(erbs, erb_scale.f_to_erb(lf))
		if etmp is not None:
			pylab.axhline(etmp, color='k', linewidth=2)

def pick_ticks(preferred_num, n):
	delta = int(round(n/preferred_num))
	return range(0, n, delta)


def imshow(img, y_grid=None, x_grid=None,
		nxticks=5, nyticks=5,
		xl=None, xmap=None,
		yl=None, ymap=None,
		yrange = 'data',
		title=None, interpolation='nearest'):

	if yrange == 'symabs':
		maxabs = gpkmisc.N_maximum(Num.absolute(Num.ravel(img)))
		vmin = -maxabs
		vmax = maxabs
	elif yrange == '0+':
		maxval = gpkmisc.N_maximum(Num.ravel(img))
		vmin = 0.0
		vmax = maxval
	elif yrange == 'data':
		vmax = gpkmisc.N_maximum(Num.ravel(img))
		vmin = gpkmisc.N_minimum(Num.ravel(img))

	pylab.imshow(img, vmin=vmin, vmax=vmax, interpolation=interpolation)

	pylab.xlim( 0, img.shape[1])
	pylab.ylim( 0, img.shape[0])
	xticks = pick_ticks(nxticks, img.shape[1])
	pylab.xticks(xticks, [xmap(t) for t in xticks])
	yticks = pick_ticks(nyticks, img.shape[0])
	pylab.yticks(yticks, [ymap(t) for t in yticks])
	if y_grid:
		y_grid()
	if x_grid:
		x_grid()
	if xl:
		pylab.xlabel(xl)
	if yl:
		pylab.ylabel(yl)
	if title:
		pylab.title(title)


def plot(dur, LengthFac=None, SpecExp=None, Nsv=None, DT=DT, simple=False):
	Jc = 15 + int(round(3.0*dur/0.01))
	Ebw = 0.5
	# Ebw = 1.0
	Emax = erb_scale.f_to_erb(6500.0)
	Emin = erb_scale.f_to_erb(60.0)
	# Emax = erb_scale.f_to_erb(1800.0)
	# Emin = erb_scale.f_to_erb(1000.0)
	iErb0 = int(round(Emin/Ebw))
	iErbe = int(round(Emax/Ebw))
	erbs = [ ie*Ebw for ie in range(iErb0, iErbe) ]

	def grw(erb):
		return get_response(erb, dur, ebw=Ebw,
					LengthFac=LengthFac, SpecExp=SpecExp, Nsv=Nsv,
					DT=DT, simple=simple)

	# responses = GT.map(grw, erbs)
	responses = map(grw, erbs)

	# pylab.show()
	assert len(responses) > 0
	assert len(responses[0].shape) == 2
	nf = responses[0].shape[1]
	nt = responses[0].shape[0]
	assert nf <= nt
	ne = len(responses)
	
	# maxabs = 0.0
	# for r in responses:
		# tmp = gpkmisc.N_maximum(Num.absolute(Num.ravel(r)))
		# if tmp > maxabs:
			# maxabs = tmp

	# pylab.gray()
	imsum = Num.zeros((ne,nt), Num.Float)
	for f in range(nf):
		pylab.figure(f)
		img = Num.zeros((ne,nt), Num.Float)
		for ie in range(ne):
			img[ie,:] = responses[ie][:,f]
		if gpkmisc.N_maximum(Num.ravel(img)) < -gpkmisc.N_minimum(Num.ravel(img)):
			Num.multiply(img, -1, img)

		Num.add(imsum, img**2, imsum)

		imshow(img, yrange='symabs', y_grid=lambda: freq_grid(erbs),
				xl='Time (ms)', xmap=lambda j:'%.0f' % (10.0*(j-Jc)),
				yl='Frequency (erbs)', ymap=lambda j: '%.1f'% (Ebw*(j+iErb0)),
				title='Feature %d' % f)
	pylab.figure()
	print_mean_sigma('erbs', Num.sqrt(Num.sum(imsum, axis=1)))
	print_mean_sigma('cs', Num.sqrt(Num.sum(imsum, axis=0)), dur/DT)
	imsum = Num.sqrt(imsum)
	imshow(imsum, yrange='0+', y_grid=lambda: freq_grid(erbs),
			xl='Time (ms)', xmap=lambda j:'%.0f' % (10.0*(j-Jc)),
			yl='Frequency (erbs)', ymap=lambda j: '%.1f'% (Ebw*(j+iErb0)),
			title='Imsum')
	pylab.show()


def print_mean_sigma(label, a, extra=0.0):
	t = Num.arange(a.shape[0])
	avg = Num.sum(t*a)/Num.sum(a)
	sigma = math.sqrt(Num.sum((t-avg)**2 * a)/Num.sum(a) - extra**2)
	print '#MS', label, 'mean=', avg, 'sigma=', sigma


if __name__ == '__main__':
	import sys
	arglist = sys.argv[1:]
	LengthFac = 1.0
	SpecExp = 0.0
	Nsv = 1.00
	Simple = False
	while arglist and arglist[0].startswith('-'):
		arg = arglist.pop(0)
		if arg == '--':
			break
		elif arg == '-SpecExp':
			SpecExp = arglist.pop(0)
		elif arg == '-Nsv':
			Nsv = arglist.pop(0)
		elif arg == '-LF':
			LengthFac = float(arglist.pop(0))
		elif arg == '-sfv':
			Simple = True
		elif arg == '-xform':
			XFORM = arglist.pop(0)
		else:
			die.die('Unrecognized flag: %s' % arg)
	plot(0.02, LengthFac=LengthFac, SpecExp=SpecExp, Nsv=Nsv, simple=Simple)
