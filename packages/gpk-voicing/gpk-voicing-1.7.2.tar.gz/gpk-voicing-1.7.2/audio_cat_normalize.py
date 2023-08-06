#!/usr/bin/env python

import os
import sys
import math
import gpkimgclass
from gmisclib import Num
from gmisclib import wavio
from gmisclib import gpkmisc
from gmisclib import die
from gpk_voicing import emphasis

DT = 0.03
R = 1
D = 1

if __name__ == '__main__':
	import sys
	arglist = sys.argv[1:]
	outfile = 'foo.wav'
	while arglist and arglist[0].startswith('-'):
		arg = arglist.pop(0)
		if arg == '--':
			break
		elif arg == '-stereo':
			D = 2
		elif arg == '-mono':
			D = 1
		elif arg == '-resample':
			R = int(arglist.pop(0))
		elif arg == '-o':
			outfile = arglist.pop(0)
		else:
			die.die('Unrecognized flag: %s' % arg)

	normfacs = []
	data = []
	for f in arglist:
		gotit = False
		try:
			q = gpkimgclass.read(f)
			gotit = True
		except gpkimgclass.CannotReadDataFile, x:
			die.info('File %s unreadable: %s' % (f, str(x)))
		if not gotit:
			q = wavio.read(f)

		n = 0
		s = 0.0
		for c in range(q.d.shape[1]):
			tmp = emphasis.simple_emphasis(q.column(c), q.dt(), DT)
			tt = Num.sort(Num.ravel(tmp))
			assert len(tt.shape) == 1
			if tt.shape[0] > 0:
				s += tt[int(tt.shape[0]*0.9)]
				n += 1
		assert n > 0
		# Normalize amplitudes:
		print "Loudness=", s/n
		normfac = math.pow(n/s, 1.5)
		q.d = q.d * normfac
		data.append(q)
		normfacs.append(normfac)

	normfac = gpkmisc.median(normfacs)
	for q in data:
		q.d /= normfac

	o = []
	for q in data:
		assert abs(math.log(q.dt()/data[0].dt())) < 0.0001
		if q.d.shape[1] == D:
			o.append(q.d[::R])	# Resample
		elif q.d.shape[1] == 1:		# Mono->Stereo
			tmp = Num.transpose(Num.array([q.d[::R,0]]*D))
			print "ts=", tmp.shape, "qds=", q.d.shape
			assert tmp.shape[0] == (q.d.shape[0]+R-1)/R
			assert tmp.shape[1] == D
			o.append(tmp)
		elif D == 1:		# Stereo -> Mono
			die.die('Unimplemented')
	da = Num.concatenate(o, axis=0)

	header = {'CDELT2': R*data[0].dt(), 'CRPIX2':0, 'CRVAL2':0.0}
	if outfile.endswith('.wav'):
		unwritten = True
		while unwritten:
			try:
				wavio.write(gpkimgclass.gpk_img(header, da), outfile)
				unwritten = False
			except ValueError, x:
				assert 'overflow' in str(x)
				Num.divide(da, 1.5, da)
				die.warn("Overflow on writing to .wav file.  Scaling down by factor of 1.5.")
	else:
		gpkimgclass.gpk_img(header, da).write(outfile)
