#!/usr/bin/env python
# DT Flickr Update
#
# Douglas Thrift
#
# $Id: update.py 25 2008-11-21 00:57:10Z douglas $

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

from __future__ import with_statement
from __init__ import Flickr
import optparse
import os.path

if __name__ == '__main__':
	parser = optparse.OptionParser()

	parser.add_option('-a', '--api-key', action = 'store', dest = 'api_key', help = 'Flickr API key')

	options = parser.parse_args()[0]

	if options.api_key is None:
		parser.error('-a or --api-key not specified')

	flickr = Flickr(options.api_key)
	namespaces = {}

	for method in flickr.reflection.getMethods().methods.method:
		info = flickr.reflection.getMethodInfo(method_name = method)
		namespace, method = str(method).split('.', 1)

		assert namespace == 'flickr'

		namespace, method = method.rsplit('.', 1)
		documentation = str(info.method.name).strip() + '\n\n  ' + str(info.method.description).strip()

		if len(info.arguments.argument) != 1:
			documentation += '\n\n  Arguments:'

			for argument in info.arguments.argument:
				if argument.name != 'api_key':
					documentation += '\n\n    ' + argument.name + ' ('

					if int(argument.optional) == 0:
						documentation += 'Required'
					else:
						documentation += 'Optional'

					documentation += ')\n      ' + str(argument)

		try:
			namespaces[namespace].append((method, documentation))
		except KeyError:
			namespaces[namespace] = [(method, documentation)]

	namespaces = namespaces.items()

	namespaces.sort()

	with open(os.path.join(os.path.dirname(__file__), '_methods.py'), 'wb') as python:
		python.write('# DT Flickr Methods\n#\n# Douglas Thrift\n#\n# $' + 'Id$\n\nnamespaces = (\n')

		for namespace, methods in namespaces:
			python.write('\t(\'' + namespace + '\', (\n')

			for method, documentation in methods:
				python.write('\t\t(\'' + method + '\', ' + repr(documentation) + '),\n')

			python.write('\t)),\n')

		python.write(')\n\ndef namespace(namespace):\n\treturn namespace.title().replace(\'.\', \'\')\n')
