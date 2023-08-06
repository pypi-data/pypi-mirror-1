#!/usr/bin/env python
# DT Flickr
#
# Douglas Thrift
#
# $Id: setup.py 39 2009-08-16 10:27:21Z douglas $

from setuptools import setup, find_packages

setup(
	name = 'dtflickr',
	version = '1.4',
	packages = find_packages(),
	platforms = ['any'],
	extras_require = {
		'simplejson': ['simplejson>=1.7'],
	},
	author = 'Douglas Thrift',
	author_email = 'douglas@douglasthrift.net',
	description = 'Spiffy Flickr API library using JSON',
	long_description = 'DT Flickr is a spiffy automagically built Flickr API library for Python using JSON.',
	license = 'Apache License, Version 2.0',
	keywords = 'flickr api',
	url = 'http://code.douglasthrift.net/trac/dtflickr',
	classifiers = [
		'Development Status :: 5 - Production/Stable',
		'Intended Audience :: Developers',
		'License :: OSI Approved :: Apache Software License',
		'Operating System :: OS Independent',
		'Programming Language :: Python',
		'Topic :: Multimedia :: Graphics',
		'Topic :: Software Development :: Libraries :: Python Modules',
	],
)
