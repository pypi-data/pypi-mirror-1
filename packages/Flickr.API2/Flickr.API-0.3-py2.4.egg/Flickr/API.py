#!/usr/bin/env python

"""Flickr API Acesss

General Doc: http://www.flickr.com/services/api/
Authentication Doc:  http://www.flickr.com/services/api/auth.spec.html

Sample usage:
	import Flickr.API

	# flickr.test.echo:
	api = Flickr.API.API(key, secret)
	test_response = api.execute_method(method='flickr.test.echo')
	test_response.dump()

	# flickr.auth.getFrob:
	frob_request = Flickr.API.Request(method='flickr.auth.getFrob')
	frob_response = api.execute_request(frob_request)
	if frob_response.success:
		frob = frob_response.et.findtext('frob')
	
	# get the desktop authentication url
	url = api.get_auth_url(frob, 'write')

	# ask the user to authorize your app now using that url

	# flickr.auth.getToken:
	token_response = api.execute_request(Flickr.API.Request(method='flickr.auth.getToken', frob=frob))
	if token_response.success:
		token = token_response.et.find('auth').findtext('token')

	# flickr.activity.userPhotos (requires authentication):
	activity = api.execute_request(Flickr.API.Request(method='flickr.activity.userPhotos', auth_token=token, timeframe='1d'))

	# upload
	photo = open('photo.jpg', 'rb')
	upload_request = Flickr.API.Request(url="http://api.flickr.com/services/upload", auth_token=token, title='test upload', photo=photo)
	upload_response = api.execute_request(upload_request, sign=True, encode=Flickr.API.encode_multipart_formdata)

	# or upload this way
	upload_response = api.execute_upload(filename='photo.jpg', args={'auth_token':token, 'title':'test upload', 'photo':photo})
"""

__author__ = "Gilad Raphaelli"
__version__ = "0.3"

try:
	import xml.etree.cElementTree as ET
except ImportError:
	import cElementTree as ET

import md5,mimetypes,urllib,urllib2
import API

def encode_multipart_formdata(args):
	""" Encode upload as multipart/form-data. From http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/146306 """
	BOUNDARY = '----------ThIs_Is_tHe_bouNdaRY_$'
	CRLF = '\r\n'
	L = []
	for (key, value) in args.items():
		if hasattr(value, 'read'):
			if hasattr(value, 'name'):
				filename = value.name
			elif args.has_key('title'):
				filename = args['title']
			else:
				filename = 'unknown'
			L.append('--' + BOUNDARY)
			L.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename))
			L.append('Content-Type: %s' % get_content_type(filename))
			L.append('')
			L.append(value.read())
		else:
			L.append('--' + BOUNDARY)
			L.append('Content-Disposition: form-data; name="%s"' % key)
			L.append('')
			L.append(value)
	L.append('--' + BOUNDARY + '--')
	L.append('')
	body = CRLF.join(L)
	headers = {
		'Content-Type': 'multipart/form-data; boundary=%s' % BOUNDARY,
		'Content-Length': len(body)
	}
	return (headers, body)

def encode_urlencode(args):
	return ({},urllib.urlencode(args))

def get_content_type(filename):
	return mimetypes.guess_type(filename)[0] or 'application/octet-stream'

def sign_args(secret, args):
	""" Given a Flickr API secret and an array of args including an api_key key return an api_sig (string) """
	sig = secret
	for key in sorted(args.keys()):
		sig += key
		if args[key] is not None:
			sig += str(args[key])

	return md5.new(sig).hexdigest()
	
class APIError(Exception): pass

class API:
	""" To access the Flickr API """
	def __init__(self, key, secret):
		self.key = key
		self.secret = secret

	def execute_method(self, method, args={}, sign=False):
		""" Given a Flickr API method and arguments, construct a Flickr.API.Request and return a Flickr.API.Response """
		args['method'] = method
		return self.execute_request(Request(**args), sign)

	def execute_upload(self, filename, args={}):
		try:
			photo = open(filename, mode='rb')
			args['photo'] = photo
		except IOError, (e.no, e.msg):
			raise APIError, "Unable to open %s - %s: %s" % (filename, e.no, e.msg)
			
		return self.execute_request(Request(url='http://api.flickr.com/services/upload/',**args), sign=True, encode=encode_multipart_formdata)

	def execute_request(self, request, sign=True, encode=encode_urlencode):
		""" Given a Flickr.API.Request return a Flickr.API.Response, altering the original Request """
		
		request.args['api_key'] = self.key

		if sign:
			# Sign args as they are now, except photo
			args_to_sign = {}
			for (k,v) in request.args.items():
				if k not in ('photo'):
					args_to_sign[k] = v
				
			request.args['api_sig'] = self.__sign_args(args_to_sign)

		request.add_header('Host', request.get_host())

		(headers, body) = encode(request.args)
		for (header, value) in headers.items():
			request.add_header(header, value)

		# urllib2 method goes POST when data is added (but make sure)
		request.add_data(body)
		if (request.get_method() != "POST"):
			raise Exception, "not a POST? Something is wrong here"

		response = Response(urllib2.urlopen(request))

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

class Request(urllib2.Request):
	""" A request to the Flickr API subclassed from urllib2.Request allowing for custom proxy, cache, headers, etc """
	def __init__(self, url='http://api.flickr.com/services/rest/', **args):
		urllib2.Request.__init__(self, url=url)
		self.args = args

class Response:
	""" A response from the Flickr API """
	def __init__(self, response):
		self.response = response
		self.et = ET.parse(response)

		rsp = self.et.getroot()
		if rsp.tag != "rsp":
			raise APIError, "unexpected response from Flickr API, expecting <rsp>..</rsp>, got <%s>" % (rsp.tag,)

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
	res = api.execute_method(method='flickr.test.echo', args={'foo':'bar'})

	res.dump()
