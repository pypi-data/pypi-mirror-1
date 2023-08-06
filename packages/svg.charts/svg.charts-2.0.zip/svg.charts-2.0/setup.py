#!python

# $Id: setup.py 75 2009-08-30 17:35:39Z jaraco $

from setuptools import setup, find_packages

setup(name = "svg.charts",
	version = "2.0",
	description = "Python SVG Charting Library",
	long_description = open('readme.txt').read().strip(),
	author = "Jason R. Coombs",
	author_email = "jaraco@jaraco.com",
	url = "http://py-svg.sourceforge.net",
	packages = find_packages(exclude=['tests', 'docs']),
	zip_safe=True,
	namespace_packages=['svg'],
	install_requires=[
		'python-dateutil>=1.4',
		'cssutils>=0.9.5.1',
		'lxml>=2.0',
	],
	license = "MIT",
	classifiers = [
		"Development Status :: 5 - Production/Stable",
		"Intended Audience :: Developers",
		"Intended Audience :: Science/Research",
		"Programming Language :: Python",
		"License :: OSI Approved :: MIT License",
	],
	entry_points = {
	},
	tests_require=[
		'nose>=0.10',
	],
	test_suite = "nose.collector",
	
	)

