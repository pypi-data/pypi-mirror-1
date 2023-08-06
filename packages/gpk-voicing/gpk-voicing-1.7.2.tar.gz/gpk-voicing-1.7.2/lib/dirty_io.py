
import numpy
from gmisclib import die
from gmisclib import wavio
from gmisclib import Numeric_gpk as NG

NEARCLIP = 32500

def wav_read(filename, channel=None, info={}):
	"""Quick and dirty way to read a single channel of audio from a
	multichannel file.  If the channel is not specified, either as an
	argument or as info['Channel'], then it will pick whatever channel
	has the largest amplitude.   Needless to say, this is not entirely
	reliable unless you know that the other channel is silent.
	@param channel: which channel to use?  It can be a string name, an integer column number
		or None.
	@return: a gpk_img data structure holding the audio and header information.
	@param info: a dictionary with miscellaneous metadata.   Only C{info['Channel']} is used.
	@type info: C{dict}.
	@type channel: C{string}, C{int}, or C{None}.
	"""
	if channel is None:
		channel = info.get('Channel', None)

	x = wavio.read(filename)
	trouble = []
	if channel is None and x.d.shape[1] > 1:
		assert x.d.shape[1] < 1000
		rms = NG.block_stdev(x.d)
		biggest = numpy.argmax(rms)
		x.d = x.d.take([biggest], axis=1)
		assert len(x.d.shape) == 2
		die.info('Taking data from channel %d' % biggest)
		if rms[1-biggest] > 0.1*rms[biggest]:
			die.warn('Warning: channel %d is comparable: MAD=%.2g/%.2g'
					% (1-biggest, rms[1-biggest], rms[biggest])
					)
			x.hdr['WhyAudioChannel'] = 'It was slightly louder'
			trouble.append('Ambiguous channel')
		else:
			x.hdr['WhyAudioChannel'] = 'It was much louder'
	elif channel is None and x.d.shape[1]==1:
		x.hdr['WhyAudioChannel'] = 'There was only one'
	else:
		x.d = x.d.take([channel], axis=1)
		x.hdr['WhyAudioChannel'] = 'Specified in g_audioprep.py'

	if NG.N_maximum(x.column(0)) > NEARCLIP or NG.N_minimum(x.column(0))<-NEARCLIP:
		da = numpy.absolute(x.column(0))
		die.warn("Data is near clipping: maximum abs(value)=%d, %.1f%% near clipping"
			% (NG.N_maximum(da), numpy.sum(numpy.greater(da, NEARCLIP))/float(da.shape[0])))
		trouble.append('Near clipping')

	x.hdr['Trouble'] = ','.join(trouble)
	x.hdr['AudioChannel'] = channel
	assert x.d.shape[1] == 1
	return x
