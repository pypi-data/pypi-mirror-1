#!/usr/bin/python

"""This script takes the loudest channel from a multichannel
.wav file and converts it to any format known by gpkimgclass.py
"""
from gpk_voicing import dirty_io



if __name__ == '__main__':
	import sys
	channel = None
	arglist = sys.argv[1:]
	while arglist and arglist[0].startswith('-'):
		arg = arglist.pop(0)
		if arg == '--':
			break
		elif arg == '-c':
			channel = int(arglist.pop(0))
		else:
			die.die('Unrecognized argument: %s' % arg)
	if len(arglist) != 2:
		print __doc__
		sys.exit(1)

	x = dirty_io.wav_read(arglist[0], channel)
	x.write(arglist[1])
