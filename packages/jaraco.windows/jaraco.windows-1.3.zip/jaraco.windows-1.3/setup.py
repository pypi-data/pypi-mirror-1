# -*- coding: UTF-8 -*-

""" Setup script for building jaraco.windows distribution

Copyright © 2009 Jason R. Coombs
"""

from setuptools import setup, find_packages
from jaraco.util.package import read_long_description

__author__ = 'Jason R. Coombs <jaraco@jaraco.com>'
__version__ = '$Rev: 921 $'[6:-2]
__svnauthor__ = '$Author: jaraco $'[9:-2]
__date__ = '$Date: 2009-03-15 12:23:38 -0400 (Sun, 15 Mar 2009) $'[7:-2]

name = 'jaraco.windows'

setup (name = name,
		version = '1.3',
		description = 'Windows Routines by Jason R. Coombs',
		long_description = read_long_description(),
		author = 'Jason R. Coombs',
		author_email = 'jaraco@jaraco.com',
		url = 'http://pypi.python.org/pypi/'+name,
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
