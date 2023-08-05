#!/usr/bin/env python

"""Flickr API Acesss

General Doc: http://www.flickr.com/services/api/
Authentication Doc:  http://www.flickr.com/services/api/auth.spec.html

Sample usage:
	import Flickr.API

	# flickr.test.echo:
	api = Flickr.API.API(key, secret)
	test_response = api.execute_method(method = 'flickr.test.echo')
	test_response.dump()

	# flickr.auth.getFrob:
	frob_request = Flickr.API.Request(method='flickr.auth.getFrob', args={})
	frob_response = api.execute_request(frob_request)
	if frob_response.success:
		frob = frob_response.et.findtext('frob')
	
	# get the desktop authentication url
	url = api.get_auth_url(frob, 'read')

	# ask the user to authorize your app now using that url

	# flickr.auth.getToken:
    token_response = api.execute_request(Flickr.API.Request(method='flickr.auth.getToken', args={'frob': frob}))
	if token_response.success:
		token = token_response.et.find('auth').findtext('token')

	# flickr.activity.userPhotos (requires authentication):
	activity = api.execute_request(Flickr.API.Request(method='flickr.activity.userPhotos', args={'auth_token': token, 'timeframe': '1d'}))
"""

__author__ = "Gilad Raphaelli"
__version__ = "0.1"

try:
	import xml.etree.cElementTree as ET
except ImportError:
	import cElementTree as ET

import md5,urllib,urllib2

class APIError(Exception): pass

class API:
	""" To access the Flickr API """
	def __init__(self, key, secret):
		self.key = key
		self.secret = secret

	def execute_method(self, method, args={}, sign=False):
		""" Given a Flickr API method and arguments, construct a Flickr.API.Request and return a Flickr.API.Response """
		return self.execute_request(Request(method, args), sign)

	def execute_request(self, request, sign=True):
		""" Given a Flickr.API.Request return a Flickr.API.Response, altering the original Request """
		# Do this here in case it changed after object creation
		request.args['method'] = request.method
		request.args['api_key'] = self.key

		if sign:
			# Sign args as they are now
			request.args['api_sig'] = self.__sign_args(request.args)

		# urllib2 method goes POST when data is added (but make sure)
		request.add_data(urllib.urlencode(request.args))
		if (request.get_method() != "POST"):
			raise Exception, "not a POST? Something is wrong here"

		response = Response(urllib2.urlopen(request))
		# except URLError

		if (response.response.code != 200):
			raise APIError, ("API Returned an HTTP %s code '%s'" % (response.response.code,response.response.msg), response)

		return response

	def get_auth_url(self, frob, perms):
		""" Given a frob obtained via a 'flickr.auth.getFrob' and perms (currently read, write, or delete) return a url for client api authorization """
		args = {
			'perms': perms,
			'api_key': self.key,
			'frob': frob
		}
		args['api_sig'] = sign_args(self.secret, args)

		return "http://flickr.com/services/auth/?%s" % (urllib.urlencode(args),)

	def __sign_args(self, args):
		return sign_args(self.secret, args)

def sign_args(secret, args):
	""" Given a Flickr API secret and an array of args including an api_key key return an api_sig (string) """
	sig = secret
	for key in sorted(args.keys()):
		sig += key
		if args[key] is not None:
			sig += str(args[key])

	return md5.new(sig).hexdigest()
	
class Request(urllib2.Request):
	""" A request to the Flickr API subclassed from urllib2.Request allowing for custom proxy, cache, headers, etc """
	def __init__(self, method, args={}, url='http://api.flickr.com/services/rest/'):
		urllib2.Request.__init__(self, url=url)
		self.method = method
		self.args = args

# httplib.HTTPResponse? no.
class Response:
	""" A response from the Flickr API """
	def __init__(self, response):
		self.response = response
		self.et = ET.parse(response)

		rsp = self.et.getroot()
		if rsp.tag != "rsp":
			raise APIError, "unexpected response from Flickr API, expecting <rsp>..</rsp>, got <%s>" % (rsp.tag,)
		# need to check that this is an rsp

		self.status = rsp.get("stat")
		self.success = (self.status == 'ok')

		if not self.success:
			err = rsp.find("err")
			self.error_code = err.get("code")
			self.error_msg = err.get("msg")
	
	def dump(self):
		ET.dump(self.et)
		
if (__name__ == '__main__'):
	import sys
	try:
		key = sys.argv[1]
		secret = sys.argv[2]
	except IndexError:
		print "Usage: %s <key> <secret>" % (sys.argv[0],)
		sys.exit(1)

	api = API(key, secret)
	res = api.execute_method(method = 'flickr.test.echo')

	res.dump()
