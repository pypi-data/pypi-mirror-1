#!/usr/bin/env python

from ez_setup import use_setuptools
use_setuptools ()
from setuptools import setup, find_packages

setup (
	name = 'DNSFlash',
	version = '0.2.5',
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
