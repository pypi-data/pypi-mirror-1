#!python
# from setuptools import setup, Extension

# from ez_setup import use_setuptools
# use_setuptools()
# 
# from distutils.core import setup, Extension

# This is a fancy installer that will download some missing packages.
# It's pretty good, so long as you have setuptools in your python distribution.

_imported = False
try:
	from setuptools import setup
	_imported = True
	pass
except ImportError:
	pass

#If it doesn't work, you can try the line below.   This uses the
# easy_setup.py script to download and install setuptools.
if not _imported:
	print "EZ_setup"
	try:
		from ez_setup import use_setuptools
		use_setuptools()
		from setuptools import setup
		_imported = True
		pass
	except ImportError:
		pass

# Finally, use distutils.   That should work, but you'll have to download
# all the required packages by hand.
if not _imported:
	from distutils.core import setup



setup(name = "graphite", version = "0.71",
	description = "Line and scatterplots of data, libraries and command line programs.",
	author = "Greg Kochanski",
	url = "http://graphite.sourceforge.net",
	author_email = "gpk@kochanski.org",
	packages = ["graphite"],
	package_dir = {'graphite': '.'},
	scripts = ["bin/g_multiplot", "bin/g_widthplot"],
	install_requires = [ 'numpy >= 1.0.5', 'piddle >= 1.0.15'],
	extras_require = {
			# 'TK': 'something > something'
			},
	dependency_links = ["http://sourceforge.net/project/showfiles.php?group_id=27408",
				"http://sourceforge.net/project/showfiles.php?group_id=1074"
				],
	license = 'GPL2',
	keywords = "plot scientific graphics scatterplot 3d 3D 2D 2d xy bar",
	platforms = "All",
	classifiers = [
		'License :: OSI Approved :: GNU General Public License (GPL)',
		'Operating System :: OS Independent',
		'Development Status :: 4 - Beta',
		'Topic :: Scientific/Engineering',
		'Environment :: Console',
		'Intended Audience :: End Users/Desktop',
		'Intended Audience :: Developers',
		'Intended Audience :: Science/Research',
		'Programming Language :: Python',
		'Operating System :: OS Independent',
		'Programming Language :: Python',
		'Topic :: Scientific/Engineering :: Visualization'
		],
	long_description = """Long
	"""
	)

