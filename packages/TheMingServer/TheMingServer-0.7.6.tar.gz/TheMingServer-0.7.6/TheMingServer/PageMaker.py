
# PageMaker.py
# billy_bob_ming@yahoo.com

# Copyright (C) 2005 by Richard Harris
# Released under the GNU General Public License
# (See the included COPYING file)

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.

# You should have received a copy of the GNU General Public License
# with this program; if not, write to the Free Software Foundation,
# Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

import os, sys, time
from TheMingServer import Indexer, Logger, consts, lib, debug, form
from TheMingServer.parsers import *
from TheMingServer.makers import *
from TheMingServer.writers import *

## Compression ##
try:
	import zlib
	GZIP = 1
except:
	GZIP = 0

## Module detection ##
# TheMingServer.direct_episodes
try:
	from TheMingServer.direct_episodes import *
	DIRECT_EPISODES = 1
except:
	DIRECT_EPISODES = 0
# TheMingServer.direct_sets
try:
	from TheMingServer.direct_sets import *
	DIRECT_SETS = 1
except:
	DIRECT_SETS = 0
# TheMingServer.direct_singles
try:
	from TheMingServer.direct_singles import *
	DIRECT_SINGLES = 1
except:
	DIRECT_SINGLES = 0
# TheMingServer.easy_publisher
try:
	from TheMingServer.easy_publisher import *
	EASY_PUBLISHER = 1
except:
	EASY_PUBLISHER = 0
# TheMingServer.easy_episodes
try:
	from TheMingServer.easy_episodes import *
	EASY_EPISODES = 1
except:
	EASY_EPISODES = 0


class PageMaker:
	NAME = "PageMaker"
	MENU = "menu"
	PARSERS = {
		"html":HTMLParser,
		"plain":PlainParser,
		"pre":PREParser,
		"#python":HTMLParser,
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
		"static":StaticWriter,
		"dynamic":WebWriter,
		"compressed":GZWriter,
		}

	def __init__(self, source, dest):
		self.source = source
		self.static = self.dest = dest
		self.files = {}
		self.menu = ""
		if consts.LOGGING:
			self.logger = Logger()
		if DIRECT_EPISODES:
			self.MAKERS["DirectEpisodes:html"] = DirectEpisodesMaker
			self.PARSERS["DirectEpisodes:html"] = HTMLParser
			self.MAKERS["DirectEpisodes:pre"] = DirectEpisodesMaker
			self.PARSERS["DirectEpisodes:pre"] = PREParser
		if DIRECT_SETS:
			self.MAKERS["DirectSets"] = DirectSetsMaker
			self.PARSERS["DirectSets"] = PlainParser
		if DIRECT_SINGLES:
			self.MAKERS["DirectSingles:html"] = DirectSinglesMaker
			self.PARSERS["DirectSingles:html"] = HTMLParser
			self.MAKERS["DirectSingles:pre"] = DirectSinglesMaker
			self.PARSERS["DirectSingles:pre"] = PREParser
		if EASY_EPISODES:
			self.MAKERS["EasyEpisodes:html"] = EasyEpisodesMaker
			self.PARSERS["EasyEpisodes:html"] = HTMLParser
			self.MAKERS["EasyEpisodes:pre"] = EasyEpisodesMaker
			self.PARSERS["EasyEpisodes:pre"] = PREParser
		if EASY_PUBLISHER:
			self.PARSERS["EasyPublisher:html"] = HTMLParser
			self.MAKERS["EasyPublisher:html"] = EasyPublisherMaker
			self.PARSERS["EasyPublisher:pre"] = PREParser
			self.MAKERS["EasyPublisher:pre"] = EasyPublisherMaker

	def __index(self, dirname, name):
		id = Indexer(self.static)
		self.files, self.menu = id.index(dirname, name, self.source)

	def __parse_data(self, dirname, name):
		def __read_data(fname):
			lines = lib.get_lines(fname)
			type = lines[0].strip()
			if type == "#python":
				data = []
				def w(text):
					global data
					data += (text + "\n").splitlines(1)
				namespace = globals()
				namespace["data"] = data
				namespace["write"] = w
				if "params" in form.keys():
					namespace["params"] = form["params"].value
				try: execfile(self.fname, namespace)
				except SystemExit: pass	 # in case sys.exit is called
			else: data = lines[1:]
			return type, data
		try:
			self.fname = dirname + os.sep + name
			self.title, desc = self.files[name]
			self.type, data = __read_data(self.fname)
			parser = self.PARSERS[self.type]()
			parsed_data = parser.parse(self.title, desc, data)
			parsed_data[self.MENU] = self.menu
		except:
			if debug: raise
			else: return None # this ends in a "not found" mess
		return parsed_data

	def __get_plate(self, path):
		found = 0
		if os.path.exists(path + os.sep + "site.html"):
			found = 1
			plate = path + os.sep + "site.html"
		while not found:
			path = os.path.dirname(path)
			if os.path.exists(path + os.sep + "site.html"):
				found = 1
				plate = path + os.sep + "site.html"
		if debug: print "PLATE " + path
		return plate

	def __make_page(self, parsed_data, dirname):
		if consts.PLATES:
			plate = self.__get_plate(dirname)
		else:
			plate = None
		maker = self.MAKERS[self.type](self.source)
		page = maker.make(parsed_data, plate)
		return page

	def __static_pages(self, page):
		fname = self.fname.replace(self.source, "")
		fname = self.dest + os.sep + fname + ".html"
		fname = fname.replace(os.sep, "/")
		writer = self.WRITERS["static"]()
		writer.write(fname, page)

	def __dynamic_pages(self, page):
		try:
			accepted = os.environ["HTTP_ACCEPT_ENCODING"]
		except:
			accepted = ""
		if not debug and GZIP and "gzip" in accepted:
			writer = self.WRITERS["compressed"](accepted)
		else:
			writer = self.WRITERS["dynamic"]()
		writer.write(page)

	def __log(self, dirname, name):
		dirname = dirname.replace(self.source, "")
		if dirname:
			dirname += os.sep
			if dirname[0] == os.sep:
				dirname = dirname[1:]
		self.logger.log_entry(self.title, dirname + name)

	def __write(self, page):
		if self.static:
			self.__static_pages(page)
		else:
			self.__dynamic_pages(page)

	def page(self, dirname, name):
		if self.files == {}: self.__index(dirname, name)
		if name not in self.files.keys(): return 1
		parsed_data = self.__parse_data(dirname, name)
		if parsed_data == None: return 1
		page = self.__make_page(parsed_data, dirname)
		self.__write(page)
		if consts.LOGGING:
			self.__log(dirname, name)
		return 0

	def prepal(self):
		from TheMingServer.paypal import PrePal
		p = PrePal()
		try:
			page = p.decision_page()
		except:
			if debug: raise
			else: return 1
		self.__write(page)
		return 0

	def postpal(self):
		from TheMingServer.paypal import PostPal
		p = PostPal()
		try:
			page = p.deliver()
 		except:
			if debug: raise
			else: return 1
		self.__write(page)
		return 0
