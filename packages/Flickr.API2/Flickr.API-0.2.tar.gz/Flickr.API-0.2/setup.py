#!/usr/bin/env python

import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages

setup(
	name = "Flickr.API",
	version = "0.2",
	packages = find_packages(),

	author = "Gilad Raphaelli",
	author_email = "gilad@raphaelli.com",
	description = "A Python interface to the Flickr API",
	keywords = "flickr api",
	license = "Python",
	long_description = """Based on the Flickr::API perl module,
	http://search.cpan.org/~iamcal/Flickr-API-0.08/lib/Flickr/API.pm, this
	package implements an interface to the Flickr API, defined at
	http://flickr.com/services/api/ using standard library modules (as of
	python 2.5).""",
	url = "http://raphaelli.com",
)
