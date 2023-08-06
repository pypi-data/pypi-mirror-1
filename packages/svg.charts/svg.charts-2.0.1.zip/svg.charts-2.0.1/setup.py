#!python

# $Id: setup.py 82 2009-09-01 03:53:43Z jaraco $

from setuptools import setup, find_packages

setup(name = "svg.charts",
	version = "2.0.1",
	description = "Python SVG Charting Library",
	long_description = open('readme.txt').read().strip(),
	author = "Jason R. Coombs",
	author_email = "jaraco@jaraco.com",
	url = "http://py-svg.sourceforge.net",
	packages = find_packages(exclude=['tests', 'docs']),
	zip_safe=True,
	namespace_packages=['svg'],
	include_package_data = True,
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

