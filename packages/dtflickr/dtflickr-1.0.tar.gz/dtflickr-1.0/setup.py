#!/usr/bin/env python
# Flickr API
#
# Douglas Thrift
#
# $Id: setup.py 18 2008-08-19 22:44:04Z douglas $

from setuptools import setup, find_packages

setup(
	name = 'dtflickr',
	version = '1.0',
	packages = find_packages(),
	platforms = ['any'],
	install_requires = ['simplejson>=1.7'],
	author = 'Douglas Thrift',
	author_email = 'douglas@douglasthrift.net',
	description = 'Spiffy Flickr API library using JSON',
	long_description = 'DT Flickr is a spiffy automagically built Flickr API library for Python using JSON.',
	license = 'Apache License, Version 2.0',
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
