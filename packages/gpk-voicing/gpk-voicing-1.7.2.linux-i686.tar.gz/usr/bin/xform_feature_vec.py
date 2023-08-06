#!/usr/bin/python

"""This simulates re-running feature_vec.py with the -xform or -XFORM flags.
It reads in a feature vector, then transforms it by a matrix multiplication,
and writes it back out.
"""

import os
import sys
import math
from gmisclib import chunkio
from gmisclib import die
import gpkimgclass
from gmisclib import avio
from gmisclib import Num
# from gpk_voicing import feature_vec as FV

PLOT = False

XFORM = None


def fiddle(h):
	o = {}
	for (k, v) in h.items():
		if k.startswith('F_INFO'):
			o['OLD_%s' % k] = v
		elif k.startswith('RMS'):
			pass
		elif k.startswith('TTYPE'):
			pass
		elif k.startswith('TUNITS'):
			pass
		else:
			o[k] = v
	return o


def process(d, Xform):
	fac = chunkio.datachunk(open(Xform, 'r')).read_NumArray()
	o = Num.matrixmultiply(data.d, fac)
	hdr = fiddle( data.hdr )
	hdr['XFORM'] = Xform
	for i in range( fac.shape[1] ):
		hdr['TTYPE%d' % (i+1)] = 'Mixture%d' % i
		d = ','.join(['%g' % q for q in fac[:,i] ])
		hdr['F_INFO%d' % (i+1)] = d
		hdr['RMS%d' % (i+1)] = math.sqrt(Num.average(o[:,i]**2)) 
	gpkimgclass.gpk_img(hdr, o).write(ofile)



if __name__ == '__main__':
	ofile = '-'
	arglist = sys.argv[1:]
	while arglist and arglist[0].startswith('-'):
		arg = arglist.pop(0)
		if arg == '--':
			break
		elif arg == '-o':
			ofile = arglist.pop(0)
		elif arg == '-xform':
			fxd = os.environ['OXIVOICE']
			XFORM = '%s/xform.chunk' % fxd
		elif arg == '-Xform':
			XFORM = arglist.pop(0)
		else:
			die.die('Unrecognized flag: %s' % arg)
	assert XFORM, "Nothing to do!"
	fname = arglist[0]
	data = gpkimgclass.read(fname)
	process(data, XFORM)
