#!python

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



setup(name = "gmisclib", version = "0.64.9",
	description = "Various Python Libraries, mostly scientific purposes",
	author = "Greg Kochanski",
	url = "http://kochanski.org/gpk/code/speechresearch/gmisclib",
	author_email = "gpk@kochanski.org",
	packages = ['gmisclib'],
	package_dir = {'gmisclib': '.'},
	scripts = ["bin/select_fiat_entries.py", 'bin/gpk_wavio.py'],
	install_requires = [
				# 'numpy >= 1.0.3',
				],
	extras_require = {'trimmed_mean': 'gpk_avg_py >= 1.0',
				'IO': 'gpk_img_python >= 1.2'},
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
		'Intended Audience :: Science/Research',
		'Programming Language :: Python',
		# X11
		'Operating System :: OS Independent',
		'Programming Language :: Python',
		],
	long_description = """Various Python Libraries, mostly scientific purposes.
	See http://kochanski.plus.com/code/speechresearch/gmisclib for documentation
	and http://sourceforge.net/projects/speechresearch for downloads,
	or look on the Python Cheese shop, http://pypi.python.org .
	"""
	)

