#!/usr/bin/env python

"""Computes a measure of the peakiness of the waveform.
This is large for pulse trains, and small for hiss-like
signals.
"""


import sys
import math
from gmisclib import Num
from gmisclib import die

from gpk_voicing import RMSlib
from gpk_voicing import power



DT = 0.01	# Seconds.  Default output sampling interval.
HPF = 40.0	# Hz
Final_Smooth_Width = 0.030
SilenceTune = 0.85
DTSMOOTH1 = math.sqrt(Final_Smooth_Width**2 - DT**2/12.0)
DTSMOOTH2 = math.sqrt((SilenceTune*Final_Smooth_Width)**2 - DT**2/12.0)



def peakiness(data, dt, Dt, Hpf):
	EPS = 1e-6
	avd = RMSlib.compute_intensity(data, dt, Dt, 'avd', Hpf,
					DTSmooth=DTSMOOTH1)
	aavd = Num.sum(avd)/avd.shape[0]
	rms = RMSlib.compute_intensity(data, dt, Dt, 'rms', Hpf,
					DTSmooth=DTSMOOTH2)
	return Num.minimum(1.0, Num.log(Num.maximum(1.0, rms/(avd + EPS*aavd))))


if __name__ == '__main__':
	import gpkimgclass
	arglist = sys.argv[1:]
	columns = None
	signalfile = None
	outfile = None
	extrahdr = {}
	while len(arglist)>0 and arglist[0][0]=='-':
		arg = arglist.pop(0)
		if arg == '-c':
			if columns == None:
				columns = []
			tmp = arglist.pop(0)
			try:
				col = int(tmp)
			except ValueError:
				col = tmp
			columns.append(col)
		elif arg == '-f':
			signalfile = arglist.pop(0)
			die.note("signalfile", signalfile)
		elif arg == '-o':
			outfile = arglist.pop(0)
		elif arg == '-dt':
			DT = float(arglist.pop(0))
			assert DT>0.0, 'Silly time step.'
		elif arg == '-hpf':
			HPF = float(arglist.pop(0))
			assert HPF > 0.0, "Silly highpass frequency"
		elif arg == '-write':
			extrahdr = dict( [q.strip().split('=', 1)
					for q in arglist.pop(0).split(';') ]
					)
		else:
			die.die("Unrecognized flag: %s" % arg)
	if len(arglist) > 0:
		rootname = arglist.pop(0)
		if signalfile == None:
			signalfile = rootname + '.d'
		if outfile == None:
			outfile = '%s.pkns.dat' % rootname
	if outfile == None:
		outfile = 'pkns.dat'
	signal = gpkimgclass.read(signalfile)
	nch = signal.d.shape[1]
	if columns == None:
		columns = range(nch)
	die.note("columns", str(columns))
	for c in columns:
		try:
			signal.column(c)
		except KeyError:
			die.info("File has %d columns" % signal.n[1])
			die.die("Bad column: %s" % str(c))

	tmp = [
		peakiness(signal.column(i), signal.dt(), DT, HPF)
			for i in columns
		]
	n = len(tmp[0])
	o = Num.zeros((n,), Num.Float)
	for t in tmp:
		Num.add(o, t, o)
	o = o / nch

	hdr = signal.hdr.copy()
	hdr['CDELT2'] = DT
	hdr['CRPIX2'] = 0
	hdr['CRVAL2'] = signal.start()
	hdr['CDELT1'] = 1
	hdr['TTYPE1'] = 'peakiness'
	hdr['BITPIX'] = -32
	hdr.update( extrahdr )
	oo = gpkimgclass.gpk_img(hdr, Num.transpose( [o]))
	oo.write(outfile)

