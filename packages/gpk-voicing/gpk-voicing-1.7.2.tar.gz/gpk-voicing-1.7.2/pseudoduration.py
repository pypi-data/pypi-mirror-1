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

import sys
import math as M
import numpy
from gmisclib import die
import gpk_voicing.fv_misc as FVM
import gpkimgclass
from gpk_voicing import pseudo_dur as PD
from gpk_voicing import fv_pdur as FVP

C = 10.2
Lfac = 1.03
TYP_DUR = 0.1	# Seconds

def pdur(data, dt, Dt, out, c=None, lfac=None):
	# print 's.n=', data.shape
	sp, descr, t0 = FVP.feature_vec(data, dt, Dt, Nsv=FVM.NSV)
	nfvc = len(sp)
	sp = numpy.transpose(sp)
	assert sp.shape[1] == nfvc

	ns = sp.shape[0]
	assert abs(ns*Dt - data.shape[0]*dt) < 0.1*ns*Dt
	o = numpy.zeros((ns,), numpy.float)
	for i in range(ns):
		plp, pcp = PD.pdur_guts(sp, i, 1, Dt, c)
		plm, pcm = PD.pdur_guts(sp, i, -1, Dt, c)
		if out=='pseudoduration':
			o[i] = lfac * (plp + plm)
		elif out=='log(pseudoduration)':
			o[i] = M.log((lfac/TYP_DUR) * (plp + plm))
		elif out=='center_time':
			o[i] = Dt*(pcp + pcm)/(plp+plm)
		else:
			die.die('Whoops: out=%s' % out)
	return o


if __name__ == '__main__':
	# try:
		# import psyco
		# psyco.full()
	# except ImportError:
		# pass

	DT = 0.01	# Seconds.  Default output sampling interval.
	arglist = sys.argv[1:]
	arglist0 = arglist
	column = None
	signalfile = None
	outfile = None
	extrahdr = {}
	RTYPE = 'pseudoduration'
	while arglist and arglist[0].startswith('-'):
		arg = arglist.pop(0)
		if arg == '--':
			break
		elif arg == '-DT' or arg == '-dt':
			DT = float(arglist.pop(0))
		elif arg == '-f':
			signalfile = arglist.pop(0)
		elif arg == '-c' or arg == '-col':
			tmp = arglist.pop(0)
			try:
				column = int( tmp )
			except ValueError:
				column = tmp
			die.note("signalfile", signalfile)
		elif arg == '-lfac':
			LFAC = M.exp(float(arglist.pop(0)))
		elif arg == '-C':
			C = float(arglist.pop(0))
		elif arg == '-dur':
			RTYPE = 'pseudoduration'
		elif arg == '-logdur':
			RTYPE = 'log(pseudoduration)'
		elif arg == '-ctr':
			RTYPE = 'center_time'
		elif arg == '-o':
			outfile = arglist.pop(0)
		elif arg == '-write':
			extrahdr = dict( [q.strip().split('=', 1)
					for q in arglist.pop(0).split(';') ]
					)
		else:
			die.info("Unrecognized flag: %s" % arg)
			print __doc__
			die.exit(1)
	if arglist and signalfile is None:
		signalfile = arglist.pop(0)
	if arglist and outfile is None:
		outfile = arglist.pop(0)
	elif outfile is None:
		outfile = 'pdur.dat'
	if column is None:
		column = 0
	if signalfile is None:
		die.info("No signal file specified.")
		print __doc__
		die.exit(1)
	if arglist:
		die.info('Extra arguments!')
		print __doc__
		die.exit(1)
	signal = gpkimgclass.read(signalfile)
	try:
		signal.column(column)
	except KeyError:
		die.info("File has %d columns" % signal.n[1])
		die.die("Bad column: %s" % str(column))

	try:
		o = pdur(signal.column(column), signal.dt(), DT, RTYPE, c=C, lfac=Lfac)
	except:
		die.catch("Exception in pdur calculation")
		raise

	hdr = signal.hdr.copy()
	hdr['program'] = sys.argv[0]
	hdr['ARGV'] = arglist0
	hdr['input_file'] = signalfile
	hdr['column'] = column
	hdr['CDELT2'] = DT
	hdr['CRPIX2'] = 1
	hdr['CRVAL2'] = signal.start()
	hdr['CDELT1'] = 1
	hdr['TTYPE1'] = RTYPE
	hdr['BITPIX'] = -32
	hdr['DataSamplingFreq'] = 1.0/signal.dt()
	hdr.update( extrahdr )
	gpkimgclass.gpk_img(hdr, o).write(outfile)
