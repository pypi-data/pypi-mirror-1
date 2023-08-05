#!python
from setuptools import setup
# from ez_setup import use_setuptools
# use_setuptools()

# from distutils.core import setup, Extension


setup(name = "voicing", version = "0.51",
	description = "Speech signal processing libraries and scripts.",
	author = "Greg Kochanski",
	url = "http://kochanski.org/gpk/code/speechresearch/voicing",
	author_email = "gpk@kochanski.org",
	packages = ['voicing'],
	package_dir = {'voicing': 'lib'},
	scripts = ['emphasis_stevens.py'],
	install_requires = [
				'numpy >= 1.0.3',
				'gmisclib >= 0.51',
				],
	extras_require = {},
	dependency_links = [
				],
	license = 'GPL2',
	keywords = "phonetics speech computational linguistics basic library python science optimize",
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
	long_description = """Long
	"""
	)

