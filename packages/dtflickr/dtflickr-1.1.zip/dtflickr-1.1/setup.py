#!/usr/bin/env python
# Flickr API
#
# Douglas Thrift
#
# $Id: setup.py 22 2008-09-08 00:29:00Z douglas $

from setuptools import setup, find_packages

setup(
	name = 'dtflickr',
	version = '1.1',
	packages = find_packages(),
	platforms = ['any'],
	install_requires = ['simplejson>=1.7'],
	author = 'Douglas Thrift',
	author_email = 'douglas@douglasthrift.net',
	description = 'Spiffy Flickr API library using JSON',
	long_description = 'DT Flickr is a spiffy automagically built Flickr API library for Python using JSON.',
	license = 'Apache License, Version 2.0',
	keywords = 'flickr api',
	requires = ['simplejson (>=1.7)'],
	url = 'http://svn.douglasthrift.net/trac/dtflickr',
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
