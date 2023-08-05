# encoding: utf-8

from setuptools import setup, find_packages
from turbogears.finddata import find_package_data

import os
execfile(os.path.join("turbomail", "release.py"))

setup(
		name="TurboMail",
		version=version,
	
		description=description,
		author=author,
		author_email=email,
		url=url,
		download_url=download_url,
		license=license,
	
		install_requires = ["TurboGears >= 1.0b1",],
		zip_safe=True,
		packages=find_packages(),
		package_data = find_package_data(where='turbomail', package='turbomail'),
		keywords = ["turbogears.extension"],
		classifiers = [
			'Development Status :: 4 - Beta',
			'Operating System :: OS Independent',
			'Programming Language :: Python',
			'Topic :: Software Development :: Libraries :: Python Modules',
			'Framework :: TurboGears',
		],
		test_suite = 'nose.collector',
		entry_points = {'turbogears.extensions': ["turbomail = turbomail"]}
	)
	
