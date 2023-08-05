
# PageMaker.py is part of The Ming Server
# billy-bob@billy-bob-ming.com

# Copyright (C) 2005, 2006  Richard Harris, Marco Rimoldi
# Released under the GNU General Public License
# (See the included COPYING file)

# The Ming Server is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# The Ming Server is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with The Ming Server; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import os
from TheMingServer import Indexer, Logger, localizer, consts, lib, exceptions
from TheMingServer.parsers import *
from TheMingServer.makers import *
from TheMingServer.writers import *

## Compression ##
try:
	import zlib
	GZIP = 1
except:
	GZIP = 0

lib.prn(__name__, "init")

class PageMaker:
	NAME = "PageMaker"
	MENU = "menu"
	FOOTER = "footer"
	PARSERS = {
		"html":HTMLParser,
		"plain":PlainParser,
		"pre":PREParser,
		"#python":PythonParser,
		"3tml":TTMLParser,
		}
	MAKERS = {
		"html":HTMLMaker,
		"plain":HTMLMaker,
		"pre":HTMLMaker,
		"#python":HTMLMaker,
		"3tml":HTMLMaker,
		}
	WRITERS = {
		"default":WebWriter,
		"compressed":GZWriter,
		}

	def __init__(self):
		self.files_index = {}
		self.menu = ""

	def load_package(self, packname):
		lib.prn("page requires the add-on package '%s'" % packname, "INFO")
		exec "from %s import *" % packname in globals()
		for set in ("PARSERS", "MAKERS", "WRITERS"):
			try:
				exec "self.%(set)s['%(type)s'] = %(set)s['%(type)s']" % {'set': set, 'type': self.content_type}
			except:
				lib.prn("the %s package does not define %s for %s pages" % (packname, set, self.content_type),
						"WARNING")

	def __read_data(self):
		lines = lib.get_lines(self.resource)
		if not lines: # we don't have read-access to this file (or it happens to be empty)
			raise exceptions.ForbiddenError
		header = lines[0].strip()
		if ";" in header:
			header, locales = lib.tokens(header, ";")
			lines = localizer.get_resource(self.resource, locales)
		if ":" in header:
			package, header = lib.tokens(header, ":")
			self.content_type = header
			self.load_package(package)
		else:
			self.content_type = header
		lib.prn("page type is '%s'" % self.content_type, "INFO")
		return lines[1:]

	def __parse_data(self, dirname, fname):
		data = self.__read_data()
		self.title, desc = self.files_index[fname]
		parser = self.PARSERS[self.content_type]()
		parsed_data = parser.parse(self.title, desc, data)
		parsed_data[self.MENU] = self.menu
		footer = lib.get_plate("footer.html", dirname)
		parsed_data[self.FOOTER] = footer
		return parsed_data

	def __make_page(self, parsed_data, dirname):
		maker = self.MAKERS[self.content_type](dirname)
		page = maker.make(parsed_data)
		return page

	def __write(self, page):
		accepted = os.environ.get("HTTP_ACCEPT_ENCODING", "").split(",")
		if GZIP and "gzip" in accepted:
			writer = self.WRITERS["compressed"](accepted)
		else:
			writer = self.WRITERS["default"]()
		writer.write(page)

	def make(self, resource):
		self.resource = resource
		if not os.path.isfile(resource):
			raise exceptions.NotFoundError
		dirname, filename = os.path.split(resource)
		self.files_index, self.menu = Indexer().index(dirname, filename)
		if filename not in self.files_index:
			raise exceptions.ForbiddenError
		parsed_data = self.__parse_data(dirname, filename)
		page = self.__make_page(parsed_data, dirname)
		self.__write(page)
		if consts.LOGGING:
			logger = Logger()
			logger.log_entry(self.title, resource)

	def prepal(self):
		from TheMingServer.paypal import PrePal
		p = PrePal()
		page = p.decision_page()
		self.__write(page)

	def postpal(self):
		from TheMingServer.paypal import PostPal
		p = PostPal()
		page = p.deliver()
		self.__write(page)