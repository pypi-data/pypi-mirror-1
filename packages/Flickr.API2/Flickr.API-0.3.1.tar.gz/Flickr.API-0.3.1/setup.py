from distutils.core import setup

if __name__ == '__main__':
	import sys

	setup(
		name = 'Flickr.API',
		version = '0.3.1',

		author = "Gilad Raphaelli",
		author_email = "gilad@raphaelli.com",
		description = "A Python interface to the Flickr API",
		keywords = "flickr api",
		license = "Python",
		long_description = """Based on the Flickr::API perl module, this
package implements an interface to the Flickr API, defined at
http://flickr.com/services/api/.""",
		platforms = 'any',
		packages = ['Flickr'],
		url = "http://raphaelli.com",
		classifiers = [
			"Development Status :: 4 - Beta",
			"Intended Audience :: Developers",
			"Operating System :: OS Independent",
			"Programming Language :: Python",
			"Topic :: Software Development :: Libraries :: Python Modules",
		]
	)
