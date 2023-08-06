#!/usr/bin/env python

from ez_setup import use_setuptools
use_setuptools ()
from setuptools import setup, find_packages

# This is nice, but won't work on Python 2.3 :(
#import subprocess
#pkgver = subprocess.Popen (["./dnsflash.py", "--version"],
#                stdout = subprocess.PIPE).communicate()[0].strip ()
pkgver = "0.3.0"

setup (
	name = 'DNSFlash',
	version = pkgver,
#	packages = find_packages (),
	scripts = ['dnsflash.py'],
	py_modules = ['dnsomatic_api'],

	include_package_data = True,
#	package_data = {
#        	# If any package contains *.conf.sample files, include them
#		'': ['*.conf.sample']
#	},

	zip_safe = True,

	# metadata for upload to PyPI
	author = 'SukkoPera',
	author_email = 'software@sukkology.net',
	description = 'Update IP on the DNS-O-Matic service',
	url = 'http://www.sukkology.net',
	license = "GPLv2",
	keywords = "dnsomatic opendns cjb dyndns",
	# could also include long_description, download_url, classifiers, etc.

	entry_points = {
		'console_scripts': [
			'dnsflash = dnsflash:main'
		],
		'setuptools.installation': [
			'eggsecutable = dnsflash:main',
		]
	}
)
