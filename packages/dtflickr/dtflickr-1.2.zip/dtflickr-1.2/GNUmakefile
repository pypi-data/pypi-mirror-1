# DT Flickr
#
# Douglas Thrift
#
# $Id: GNUmakefile 26 2008-11-21 01:03:54Z douglas $

setup := $(CURDIR)/setup.py

.PHONY: all binary build clean register source

all: build

binary:
	$(setup) bdist --formats egg,wininst

build:
	$(setup) build

clean:
	$(setup) clean

register:
	$(setup) register

source:
	$(setup) sdist --formats bztar,gztar,zip
