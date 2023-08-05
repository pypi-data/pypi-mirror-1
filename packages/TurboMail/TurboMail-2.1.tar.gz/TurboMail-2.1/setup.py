#!/usr/bin/env python
# encoding: utf-8

import sys
from setuptools import setup, find_packages
from turbogears.finddata import find_package_data

if sys.version_info < (2, 3):
    raise SystemExit("Python 2.3 or later is required")

import os
execfile(os.path.join("turbomail", "release.py"))

setup(
		name="TurboMail",
		version=version,
	
		description=description,
		long_description=long_description,
		author=author,
		author_email=email,
		url=url,
		download_url=download_url,
		license=license,
	
		install_requires = ["TurboGears >= 0.9a9dev-r2003"],
		zip_safe=True,
		packages=find_packages(),
		package_data = find_package_data(where='turbomail', package='turbomail'),
		keywords = ["turbogears.extension"],
		classifiers = [
			'Development Status :: 5 - Production/Stable',
			'Framework :: TurboGears',
			'Intended Audience :: Developers',
			'License :: OSI Approved :: MIT License',
			'Operating System :: OS Independent',
			'Programming Language :: Python',
			'Topic :: Communications :: Email',
			'Topic :: Software Development :: Libraries :: Python Modules',
		],
		test_suite = 'nose.collector',
		entry_points = {
#				'paste.paster_create_template': ["turbomail = turbomail.startup:MailTemplate"]
				'turbogears.extensions': ["turbomail = turbomail"]
			}
	)
	
