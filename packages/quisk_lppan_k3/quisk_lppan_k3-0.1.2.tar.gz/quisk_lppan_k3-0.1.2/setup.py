try:
    from setuptools import setup, Extension
except ImportError:
    from distutils.core import setup, Extension

import _tkinter		# Read the Tk version used by _tkinter

# You must define the version here.  A title string including
# the version will be written to __init__.py and read by quisk.py.

VERSION = '0.1.2'
QUISK_VERSION = '3.0.0'
RIGCONTROL_VERSION = '0.3.5'

fp = open("__init__.py", "w")	# write title string
fp.write("#QUISK-LPPAN-K3 version %s\n" % VERSION)
fp.close()

setup	(name = 'quisk_lppan_k3',
	version = VERSION,
        install_requires = [ "quisk >= %s" % (QUISK_VERSION), "rigcontrol >= %s" % (RIGCONTROL_VERSION) ],
	description = 'Hardware support for QUISK for the Elecraft K3, LP-PAN Panadapter, and fldigi',
	long_description = """        This package provides hardware support for the Elecraft K3,
        the LP-PAN Panadapter, and the fldigi digimode program.
""",
	author = 'Leigh L. Klotz, Jr.',
	author_email = 'Leigh@WA5ZNU.org',
	url='http://wa5znu.org/2009/04/quisk-lppan-k3/',
	license="GPL",
	platforms = ['POSIX'],
	zip_safe = False,	# Do not require pkg_resources to be available
	packages=['quisk_lppan_k3'],
	package_dir = {'quisk_lppan_k3' : '.'},
	include_package_data = True,	# Add names from MANIFEST.in
	classifiers = [
		'Development Status :: 3 - Alpha',
		'Environment :: X11 Applications',
		'Intended Audience :: End Users/Desktop',
		'License :: OSI Approved :: GNU General Public License (GPL)',
		'Natural Language :: English',
		'Operating System :: POSIX',
		'Programming Language :: Python',
		'Topic :: Communications :: Ham Radio',
	],
)


