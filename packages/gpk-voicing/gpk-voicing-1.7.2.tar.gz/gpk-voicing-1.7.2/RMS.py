#!/usr/bin/env python

"""RMS or peak amplitude time series."""


import sys
import numpy
from gmisclib import die
from gpk_voicing import RMSlib

# import is_voiced



DR = 'rms'
DTSMOOTH = 0.015
DT = 0.01	# Seconds.  Default output sampling interval.
HPF = 40.0	# Hz
PKWDT = 0.020	# Full-width of window for computing peak amplitude.



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
		elif arg == '-pkpk':
			DR = 'pkpk'
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
			outfile = '%s.%s.dat' % (rootname, DR)
	if outfile == None:
		outfile = '%s.dat' % DR
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

	tmp = []
	t00 = None
	for i in columns:
		tmpR, t0 = RMSlib.compute_intensity(signal.column(i),
							signal.dt(),
							DT, DR, HPF,
							DTSmooth=DTSMOOTH)
		tmp.append( tmpR )
		if t00 == None:
			t00 = t0
		else:
			assert abs(t00-t0)/DT < 0.001
	n = len(tmp[0])
	o = numpy.zeros((n,))
	for t in tmp:
		numpy.add(o, t, o)
	o = o / nch

	hdr = signal.hdr.copy()
	hdr['CDELT2'] = DT
	hdr['CRPIX2'] = 0
	hdr['CRVAL2'] = signal.start() + t0
	hdr['CDELT1'] = 1
	hdr['TTYPE1'] = DR
	hdr['BITPIX'] = -32
	hdr.update( extrahdr )
	oo = gpkimgclass.gpk_img(hdr, numpy.transpose( [o]))
	oo.write(outfile)

