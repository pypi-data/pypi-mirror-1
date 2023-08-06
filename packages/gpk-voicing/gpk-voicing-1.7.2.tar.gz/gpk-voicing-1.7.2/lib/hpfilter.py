#!/usr/bin/env python


import gpkimgclass

import sys
import os
import voice_misc


if __name__ == '__main__':
	cutoff_freq = float(sys.argv[1])
	assert cutoff_freq > 0

	d = gpkimgclass.read(sys.argv[2])
	print 'shape=', d.d.shape
	filtered = voice_misc.hipass_sym_butterworth(d.d[:,0], cutoff_freq*d.dt(), order=4)
	gpkimgclass.gpk_img(d.hdr, filtered).write(sys.argv[3])
