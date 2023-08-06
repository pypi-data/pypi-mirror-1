#!/usr/bin/env python

"""Perceptual loudness measurement.
This is an implementation of
"Percieved Level of Noise by Mark VII and Decibels (E)"
S. S. Stevens,
J. Acoustical Soc. Am. v. 51(2, part 2) 1972
pages 575-602.

The algorithm matches the paper for FractOct==ThirdOct or OneOct.
The algorithm assumes that the level defined by SIXTY_EIGHT
corresponds to 68dB relative to 20 micro-Newtons per square meter
sound pressure.

USER INFORMATION:

You'll find, somewhere, a subdirectory named
speechresearch/voicing .
Within this is a script called emphasis_stevens.py .
This can be run as
python emphasis_stevens.py -o outputfile -write BITPIX=0 -c channelnumber inputfile
(there are a couple of other flags, too).

It will then read the input file (which is an audio recording)
and produce a time-series of the loudness.   Data input and
output is via the gpkio library, in .../speechresearch/gpkio.
That library has many virtues, but reading WAV files is not
one of them, so you have to convert .wav files to
the "GPK ASCII image" format (or one of several other formats),
using  .../speechresearch/lib/wavio.py .

The output will be in an ASCII version of the format,
which should be reasonably intelligible.    (The GPK ASCII image
format is based on the FITS astronomy format from NASA.)

However, that script uses the gpkio and gpklib libraries
(also under ../speechresearch).  These need to be compiled,
and it uses the gpk_img_python package that needs to be
installed via   "python setup.py install".
Oh, and .../speechresearch/gmisclib needs to be in
your PYTHONPATH.

Give it a try, and I'll be happy to help, and will
incorporate the troubles you have into some form of
documentation.    Sorry, I have nothing better yet.
"""

import sys
import gpkimgclass
from gmisclib import Num
from gmisclib import die
from gpk_voicing import emphasis


if __name__ == '__main__':
	DT = 0.01	# Seconds.  Default output sampling interval.
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
		elif arg == '-cal':
			emphasis.SIXTY_EIGHT = float(arglist.pop(0))
		elif arg == '-f':
			signalfile = arglist.pop(0)
			die.note("signalfile", signalfile)
		elif arg == '-o':
			outfile = arglist.pop(0)
		elif arg == '-dt':
			DT = float(arglist.pop(0))
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
			outfile = rootname + '.emph.dat'
	if outfile == None:
		outfile = 'emph.dat'
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

	tmp = [ emphasis.simple_emphasis(signal.column(i), signal.dt(), DT)
			for i in columns ]
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
	hdr['TTYPE1'] = 'loudness'
	hdr['BITPIX'] = -32
	hdr.update( extrahdr )
	oo = gpkimgclass.gpk_img(hdr, Num.transpose( [o]))
	oo.write(outfile)

