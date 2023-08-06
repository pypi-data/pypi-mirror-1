#!/usr/bin/env python

import os
import sys
import math as M
from gmisclib import Num
from gmisclib import die
# from gmisclib import erb_scale
from gmisclib import avio
import gpkavg
import gpkimgclass

# from gpk_voicing import percep_spec
# from gpk_voicing import voice_misc
from gpk_voicing import fv_misc as FVM
# import irregularity
# sys.path.insert(0, '%s/tick1/bin' % os.environ['MRImodel'])

if 'PYLABDISP' in os.environ:
	if os.environ['PYLABDISP'] == 'pylab':
		import pylab
	else:
		import g_pylab as pylab
	PLOT = True
else:
	PLOT = False




# SpecExp = 0.0




def average(x):
	vv = []
	ww = []
	for (v,wt) in x:
		vv.append(v)
		ww.append(wt)
	return gpkavg.avg(vv, ww, 0.0)[0]

def median(x):
	vv = []
	ww = []
	for (v,wt) in x:
		vv.append(v)
		ww.append(wt)
	return gpkavg.avg(vv, ww, 0.499)[0]


def weight(x):
	sum = 0.0
	for (v,wt) in x:
		sum += wt**2
	return M.sqrt(sum)


class matmult_xform(object):
	from gmisclib import chunkio
	def __init__(self, filename):
		self._name = filename
		self.xform = self.chunkio.datachunk(open(filename, 'r')).read_NumArray()

	def name(self):
		return self._name

	def describe_xform(self, descr):
		pass

	def operate(self, o, descr):
		Num.matrixmultiply(o, self.xform, o)
		for i in range(o.shape[1]):
			descr[i] = {'id': 'Mixture%d'% i}



def describe_xform(descr, fac):
	nin, nout = fac.shape
	assert len(descr) == nin
	for i in range(nout):
		norm = M.sqrt(Num.average(fac[:,i]**2))
		nf = fac[:,i]/norm
		tmp = []
		fwt = []
		wwt = []
		edginess = []
		voiciness = []
		burstiness = []
		friciness = []
		vness = []
		for j in range(nin):
			dj = descr[j]
			if dj.has_key('erb'):
				fwt.append( (dj['erb'], abs(nf[j])) )
			if dj.has_key('width'):
				wwt.append( (dj['width'], abs(nf[j])) )
			if 'edge' in dj['type']:
				edginess.append( abs(nf[j]) )
			if 'burst' in dj['type']:
				burstiness.append( abs(nf[j]) )
			if 'fricative' in dj['type']:
				friciness.append( abs(nf[j]) )
			if 'vowel' in dj['type']:
				vness.append( abs(nf[j]) )
			if 'haspitch' in dj['type']:
				voiciness.append( abs(nf[j]) )
			if abs(nf[j]) > 0.1:
				tmp.append('%+.2f*%s' % (nf[j], dj['id']) )
		print '# FV[%d]= %s' % (i, ' '.join(tmp))
		fb = {'voicing': M.sqrt(Num.sum(Num.array(voiciness)**2)),
			'edges': M.sqrt(Num.sum(Num.array(edginess)**2)),
			'burst': M.sqrt(Num.sum(Num.array(burstiness)**2)),
			'fricative': M.sqrt(Num.sum(Num.array(friciness)**2)),
			'vowel': M.sqrt(Num.sum(Num.array(vness)**2)),
			'meanfreq': average(fwt), 'medfreq': median(fwt),
			'wt_freq': weight(fwt),
			'meanwidth': average(wwt), 'medwidth': median(wwt),
			'wt_width': weight(wwt),
			'channel': i, 'description': ' '.join(tmp),
			'ltype': 'fb'
			}
		print avio.concoct(fb)




def run(argv):
	Lf = 1.5
	Elf = 1.5
	Nsv = FVM.NSV
	# Nsv and LF updated from the 5 April 2007 optimization
	# in .../m/ASR/OPT
	DT = 0.01	# Seconds.  Default output sampling interval.
	Scale = None
	arglist = argv[1:]
	arglist0 = arglist
	column = None
	signalfile = None
	outfile = None
	verbose = 0
	DoVoicing = 2
	DoDissonance = True
	import gpk_voicing.fvcurrent as fvm
	extrahdr = {}
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
		elif arg == '-o':
			outfile = arglist.pop(0)
		elif arg == '-v':
			verbose += 1
		elif arg == '-Nsv':
			FVM.NSV = float(arglist.pop(0))
		# elif arg == '-SpecExp':
			# SpecExp = float(arglist.pop(0))
		elif arg == '-sfv':
			import gpk_voicing.fvsimple as fvm
			DoVoicing = 1
		elif arg == '-ssfv':
			import gpk_voicing.fvss as fvm
			DoDissonance = False
			DoVoicing = 1
		elif arg == '-fv20071030':
			import gpk_voicing.fv20071030 as fvm
			DoVoicing = 1
		elif arg == '-fv20080325':
			import gpk_voicing.fv20080325 as fvm
			DoVoicing = 1
		elif arg == '-fv200807jyuan':
			import gpk_voicing.fv200807jyuan as fvm
			DoVoicing = 1
			DoDissonance = True
		elif arg == '-fv200811align':
			import gpk_voicing.fv200811align as fvm
			DoVoicing = 2
			DoDissonance = True
		elif arg == '-fv200812align':
			import gpk_voicing.fv200812align as fvm
			DoVoicing = 2
			DoDissonance = True
			Lf = 1.0
			Elf = 1.0
		elif arg == '-fv200908opt':
			import gpk_voicing.fv200908opt as fvm
			DoVoicing = 1
			DoDissonance = False
		elif arg.startswith('-fv200909opt'):
			import gpk_voicing.fv200909opt as fvm
			DoVoicing = 1
			DoDissonance = False
			Nsv, Lf, Elf = fvm.Scale.get_many('nsv', 'lf,lf', 'lf,elf')
			if arg.endswith('S'):
				Scale = fvm.Scale
		elif arg == '-LF':
			Lf = float(arglist.pop(0))
		elif arg == '-ELF':
			Elf = float(arglist.pop(0))
		elif arg == '-novoicing':
			DoVoicing = 0
		elif arg == '-Xform':
			Scale = matmult_xform(arglist.pop(0))
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
		outfile = 'fv.dat'
	if signalfile is None:
		die.info("No signal file specified.")
		print __doc__
		die.exit(1)
	if arglist:
		die.info('Extra arguments!')
		print __doc__
		die.exit(1)
	signal = gpkimgclass.read(signalfile)
	if column is None and signal.d.shape[1]==1:
		column = 0
	elif column is None:
		die.die("There are %d channels in %s, so you must specify one with '-c'." % (signal.d.shape[1], signalfile))
	try:
		signal.column(column)
	except KeyError:
		die.info("File has %d columns" % signal.n[1])
		die.die("Bad column: %s" % str(column))

	o, descr, DTx, tshift = fvm.feature_vec(signal.column(column), signal.dt(), DT,
					Nsv=Nsv, LF=Lf, ELF=Elf,
					do_voicing=DoVoicing,
					do_dissonance=DoDissonance
					)
	o = Num.transpose(o)
	hdr = signal.hdr.copy()
	if Scale is not None:
		Scale.operate(o, descr)
		hdr['XFORM'] = Scale.name()
		if verbose:
			Scale.describe_xform(descr)

	hdr['program'] = argv[0]
	hdr['ARGV'] = arglist0
	hdr['input_file'] = signalfile
	hdr['column'] = column
	hdr['CDELT2'] = DTx
	hdr['CRPIX2'] = 1
	hdr['CRVAL2'] = signal.start() + tshift
	hdr['CDELT1'] = 1
	hdr['BITPIX'] = -32
	hdr['DataSamplingFreq'] = 1.0/signal.dt()
	hdr['Nsv'] = FVM.NSV
	hdr['LF'] = Lf
	hdr['ELF'] = Elf
	hdr.update( extrahdr )

	if PLOT:
		pylab.matshow(Num.transpose(o))
		pylab.show()
	assert o.shape[1] == len(descr), "Length mismatch data=%s descr=%d" % (
						o.shape, len(descr)
						)
	for (i,d) in enumerate(descr):
		hdr['TTYPE%d' % (i+1)] = d['id']
		hdr['F_INFO%d' % (i+1)] = avio.concoct(d)
		hdr['RMS%d' % (i+1)] = M.sqrt(Num.average(o[:,i]**2)) 
	gpkimgclass.gpk_img(hdr, o).write(outfile)



if __name__ == '__main__':
	# try:
		# import psyco
		# psyco.full()
	# except ImportError:
		# pass

	run(sys.argv)
