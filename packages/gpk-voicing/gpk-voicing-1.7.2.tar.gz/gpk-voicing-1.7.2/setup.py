#!python

# This is a fancy installer that will download some missing packages.
# It's pretty good, so long as you have setuptools in your python distribution.

# _imported = False
# try:
	# from setuptools import setup
	# _imported = True
	# pass
# except ImportError:
	# pass
# 
# #If it doesn't work, you can try the line below.   This uses the
# # easy_setup.py script to download and install setuptools.
# if not _imported:
	# print "EZ_setup"
	# try:
		# from ez_setup import use_setuptools
		# use_setuptools()
		# from setuptools import setup
		# _imported = True
		# pass
	# except ImportError:
		# pass
# 
# # Finally, use distutils.   That should work, but you'll have to download
# # all the required packages by hand.
# if not _imported:
from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

import numpy
import os
Include_dirs = [ '.', 'lib', numpy.get_include(),
			os.path.join(os.environ['HOME'], 'local', 'include') ]
Ldirs = [ os.path.join(os.environ['HOME'], 'local', 'lib') ]

setup(name="gpk-voicing", version = "1.7.2",
	description = "Python Libraries and scripts for speech analysis.",
	author = "Greg Kochanski",
	url = "http://kochanski.org/gpk/code/speechresearch/voicing",
	author_email = "gpk@kochanski.org",
	packages = ['gpk_voicing'],
	package_dir = {'gpk_voicing': 'lib'},
	scripts = ['emphasis_stevens.py', 'feature_vec.py', 'pseudoduration.py',
			'irregularity.py', 'g_audioprep.py', 'xform_feature_vec.py',
			'audio_cat_normalize.py'
			],
	ext_modules=[ 
    		Extension("gpk_voicing.power1",         ["lib/power1.pyx"],
				include_dirs = Include_dirs,
				depends = [],
				library_dirs = Ldirs,
				libraries = ['gpk'],
				language = 'c++'
				),
    		Extension("gpk_voicing.gammatone",         ["lib/gammatone.pyx"],
				include_dirs = Include_dirs,
				depends = [],
				library_dirs = Ldirs,
				libraries = ['gpk'],
				language = 'c++'
				),
    		Extension("gpk_voicing.percep_spec_extras",         ["lib/percep_spec_extras.pyx"],
				include_dirs = Include_dirs,
				depends = [],
				library_dirs = Ldirs,
				libraries = ['gpk'],
				language = 'c++'
				),
    		Extension("gpk_voicing.power1",         ["lib/power1.pyx"],
				include_dirs = Include_dirs,
				depends = [],
				library_dirs = Ldirs,
				libraries = ['gpk'],
				language = 'c++'
				),
		],
	# install_requires = [
				# "gpkavg >= 1.0",
				# "gpkimg >= 1.2",
				# "gmisclib >= 0.60.5",
				# 'numpy >= 1.0.3',
				# ],
	cmdclass = {'build_ext': build_ext},
	# extras_require = {},
	dependency_links = [
				],
	license = 'GPL2',
	keywords = ("phonetics speech computation linguistics scripts library python "
			+ "science perception feature vector loudness spectral slope"),
	platforms = "All",
	classifiers = [
		'License :: OSI Approved :: GNU General Public License (GPL)',
		'Operating System :: OS Independent',
		'Development Status :: 3 - Alpha',
		'Topic :: Scientific/Engineering',
		'Environment :: Console',
		'Intended Audience :: Science/Research',
		'Programming Language :: Python',
		# X11
		'Operating System :: OS Independent',
		'Programming Language :: Python',
		],
	long_description = """Python Libraries for speech analysis.
	See http://kochanski.plus.com/code/speechresearch/voicing for documentation
	and http://sourceforge.net/projects/speechresearch for downloads,
	or look on the Python Cheese shop, http://pypi.python.org .
	"""
	)

