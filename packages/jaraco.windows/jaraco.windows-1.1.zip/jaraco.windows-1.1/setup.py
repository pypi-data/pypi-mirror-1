# -*- coding: UTF-8 -*-

""" Setup script for building jaraco.windows distribution

Copyright © 2009 Jason R. Coombs
"""

from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages

import pypi_fix

__author__ = 'Jason R. Coombs <jaraco@jaraco.com>'
__version__ = '$Rev: 857 $'[6:-2]
__svnauthor__ = '$Author: jaraco $'[9:-2]
__date__ = '$Date: 2009-02-24 13:50:14 -0500 (Tue, 24 Feb 2009) $'[7:-2]

setup (name = 'jaraco.windows',
		version = '1.1',
		description = 'Windows Routines by Jason R. Coombs',
		author = 'Jason R. Coombs',
		author_email = 'jaraco@jaraco.com',
		url = 'http://www.jaraco.com/projects/jaraco.windows',
		packages = find_packages(exclude=['ez_setup', 'tests', 'examples']),
		zip_safe=True,
		namespace_packages = ['jaraco',],
		license = 'MIT',
		classifiers = [
			"Development Status :: 4 - Beta",
			"Intended Audience :: Developers",
			"Programming Language :: Python",
		],
		entry_points = dict(
			console_scripts = [
				'xmouse = jaraco.windows.xmouse:run',
				'mklink = jaraco.windows.filesystem:mklink',
				'enver = jaraco.windows.environ:enver',
			],
		),
		install_requires=[
			'jaraco.util>=2.0',
		],
		extras_require = {
		},
		dependency_links = [
		],
		tests_require=[
			'nose>=0.10',
		],
		test_suite = "nose.collector",
	)
