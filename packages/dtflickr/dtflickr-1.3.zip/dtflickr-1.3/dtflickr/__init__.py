# DT Flickr
#
# Douglas Thrift
#
# $Id: __init__.py 31 2009-03-26 08:26:05Z douglas $

#  Copyright 2008 Douglas Thrift
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import hashlib
import _methods
import re
import simplejson
import time
import urllib

class Failure(Exception):
	def __init__(self, response):
		self.message = str(response.code) + ': ' + response.message

	def __str__(self):
		return self.message

class _Namespace:
	def __init__(self, flickr, namespace):
		self.__flickr = flickr
		self.__namespace = namespace

	def _execute(self, method, **arguments):
		return self.__flickr._execute(self.__namespace + '.' + method, **arguments)

for namespace, methods in _methods.namespaces:
	code = 'class ' + _methods.namespace(namespace) + '(_Namespace):\n """flickr.' + namespace + '"""\n def __init__(self, flickr):\n  _Namespace.__init__(self, flickr, \'' + namespace + '\')\n'

	for method, documentation in methods:
		code += ' def ' + method + '(self, **arguments):\n  ' + repr(documentation) + '\n  return self._execute(\'' + method + '\', **arguments)\n'

	exec code in globals(), locals()

del namespace, methods, method, documentation, code

class Flickr:
	"""Usage Example:

	  import dtflickr

	  flickr = dtflickr.Flickr(api_key)
	  response = flickr.urls.getUserPhotos(user_id = '22264298@N00')

	  print response.user.url

	  # Output:
	  #
	  # http://www.flickr.com/photos/douglaswth/
	"""

	def __init__(self, api_key, secret = None):
		"""dtflickr.Flickr

		  Flickr API

		  Arguments:

		    api_key (Required)
		      Your API application key.

		    secret (Optional)
		      Your secret for signing.
		"""
		self.__api_key = api_key

		if secret is not None:
			self.__signature = hashlib.md5()

			self.__signature.update(secret)
		else:
			self.__signature = None

		for namespace, methods in _methods.namespaces:
			exec 'self.' + namespace + ' = ' + _methods.namespace(namespace) + '(self)'

		self.__cache = {}

	def _execute(self, method, **arguments):
		for name, value in arguments.iteritems():
			arguments[name] = unicode(value).encode('utf8')

		arguments['api_key'] = self.__api_key
		arguments['format'] = 'json'
		arguments['method'] = 'flickr.' + method
		arguments['nojsoncallback'] = 1
		parameters = arguments.items()

		parameters.sort()

		if self.__signature is not None:
			signature = self.__signature.copy()

			for name, value in parameters:
				signature.update(name + unicode(value).encode('utf8'))

			parameters.append(('api_sig', signature.hexdigest()))

		parameters = urllib.urlencode(parameters)
		cached = self.__cache.get(parameters)

		if cached is not None and cached[0] > time.time():
			response = cached[1]
			now = time.time()

			for parameters, cached in self.__cache.items():
				if cached[0] <= now:
					del self.__cache[parameters]

			return response

		response = simplejson.load(urllib.urlopen('http://api.flickr.com/services/rest/', parameters), object_hook = Response)

		if response.stat == 'ok':
			self.__cache[parameters] = (time.time() + 60, response)

			return response
		else:
			raise Failure, response

class Response:
	def __init__(self, data):
		self.__data = data

	def __repr__(self):
		return str(self.__class__) + '(' + repr(self.__data) + ')'

	def __str__(self):
		return self.__data.get('_content', repr(self))

	def __getattr__(self, name):
		return self.__getitem__(name)

	def __len__(self):
		return len(self.__data)

	def __getitem__(self, name):
		return self.__data[name]

	def __iter__(self):
		return self.__data.iteritems()

	def __contains__(self, name):
		return name in self.__data

SmallSquare = 's'
Thumbnail = 't'
Small = 'm'
Medium = None
Large = 'b'
Original = 'o'

def getPhotoSourceURL(photo, size = Medium):
	"""Returns a photo source URL.

	Arguments:

	  photo (Required)
	    A photo response.

	  size (Optional)
	    A size constant (SmallSquare, Thumbnail, Small, Medium (default), Large, or Original).
	"""
	assert isinstance(photo, Response)

	url = 'http://farm' + str(photo.farm) + '.static.flickr.com/' + str(photo.server) + '/' + str(photo.id) + '_'

	if size != 'o':
		url += photo.secret

		if size is not None:
			assert size in ['s', 't', 'm', 'b']

			url += '_' + size

		url += '.jpg'
	else:
		url += photo.originalsecret + '_o.' + photo.originalformat

	return url

def getWebPageProfileURL(user_id):
	"""Returns a web page profile URL of a user.

	Arguments:

	  user_id (Required):
	    The NSID or username of the user.
	"""
	return __getWebPageURL() + 'people/' + user_id + '/'

def getWebPagePhotostreamURL(user_id):
	"""Returns a web page photostream URL of a user.

	Arguments:

	  user_id (Required)
	    The NSID or username of the user.
	"""
	return __getWebPageURL() + 'photos/' + user_id + '/'

def getBuddyiconURL(person, flickr = None):
	"""Returns a buddyicon URL for a person.

	Arguments:

	  person (Required)
	    A person response or (if the flickr argument is specified) an NSID of the user.

	  flickr (Optional)
	    A Flickr API instance used to get a person response.
	"""
	if isinstance(person, basestring):
		assert flickr is not None and isinstance(flickr, Flickr)

		person = flickr.people.getInfo(user_id = person).person

	if int(person.iconserver) > 0:
		return 'http://farm' + str(person.iconfarm) + '.static.flickr.com/' + str(person.iconserver) + '/buddyicons/' + person.nsid + '.jpg'
	else:
		return 'http://www.flickr.com/images/buddyicon.jpg'

def __getWebPageURL():
	return 'http://www.flickr.com/'

__PhotoSourceURL = re.compile(r'^http://farm([0-9]+)\.static\.flickr\.com/([0-9]+)/([0-9]+)_([a-z0-9]+)(?:(?:_([bmst]))?\.jpg|_o\.(gif|jpg|png))(?:\?.*)?$')
__WebPageURL = re.compile(r'^http://(?:www\.)?flickr\.com/(?:people|photos)/([^/]+)(?:/(?:([0-9]+)(?:/in/(?:photostream|set-([0-9]+)))?|sets(?:/([0-9]+))?))?/?(?:\?.*)?$')
__BuddyiconURL = re.compile(r'^http://farm([0-9]+)\.static\.flickr\.com/([0-9]+)/buddyicons/([^/]+)\.jpg(?:\?.*)?$')

def getURLDetails(url):
	"""Parses a Flickr URL and returns useful information from it or None if it is not a useful URL.

	This can currently parse photo source, user profile, user photos, photo, set, and buddyicon URLs.

	Arguments:
	  url (Required)
	    A Flickr URL.
	"""
	match = __PhotoSourceURL.match(url)

	if match is not None:
		if match.lastindex == 4:
			return Response({'farm': match.group(1), 'server': match.group(2), 'photo': match.group(3), 'secret': match.group(4), 'size': Medium})
		elif match.lastindex == 5:
			return Response({'farm': match.group(1), 'server': match.group(2), 'photo': match.group(3), 'secret': match.group(4), 'size': match.group(5)})
		elif match.lastindex == 6:
			return Response({'farm': match.group(1), 'server': match.group(2), 'photo': match.group(3), 'originalsecret': match.group(4), 'size': Original, 'originalformat': match.group(6)})
	
	match = __WebPageURL.match(url)

	if match is not None:
		if match.lastindex == 1:
			return Response({'user': match.group(1)})
		elif match.lastindex == 2:
			return Response({'user': match.group(1), 'photo': match.group(2)})
		elif match.lastindex == 3:
			return Response({'user': match.group(1), 'photo': match.group(2), 'photoset': match.group(3)})
		elif match.lastindex == 4:
			return Response({'user': match.group(1), 'photoset': match.group(3)})

	match = __BuddyiconURL.match(url)

	if match is not None:
		return Response({'iconfarm': match.group(1), 'iconserver': match.group(2), 'nsid': match.group(3)})

	return None
