from setuptools import setup, Extension
# from distutils.core import setup, Extension

setup(name = "graphite", version = "0.70",
	description = "Line and scatterplots of data, libraries and command line programs.",
	author = "Greg Kochanski",
	url = "http://graphite.sourceforge.net",
	author_email = "gpk@kochanski.org",
	packages = ["graphite"],
	package_dir = {'graphite': '.'},
	scripts = ["bin/g_multiplot", "bin/g_widthplot"],
	install_requires = [ 'numpy >= 1.0.1'],
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

