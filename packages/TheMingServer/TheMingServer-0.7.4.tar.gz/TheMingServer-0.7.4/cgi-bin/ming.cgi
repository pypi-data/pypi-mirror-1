#!/usr/bin/python

# ming::executable for The Ming Server
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
from TheMingServer import *

class Ming:
	NAME = "ming"
	USAGE = """
usage: %s local/dir/one local/dir/two
""" % NAME

	def __init__(self):
		if not os.path.exists(consts.FILES_DIR):
			os.makedirs(consts.FILES_DIR)
			os.chmod(consts.FILES_DIR, 0777)

	#
	# Dynamic methods
	#

	def __error(self, msg=None):
		print consts.HDR + consts.ID
		if msg == None:
			print consts.E404
		else:
			print "<h4>Error</h4>"
			print "<p>" + msg
		sys.exit()

	def __log(self):
		l = Logger()
		l.run()

	def __make_page(self, page):
		pm = PageMaker(consts.DATA, None)
		if page == "prepal":
			error = pm.prepal()
		elif page == "postpal":
			error = pm.postpal()
		else:
			dirname, name = os.path.split(page)
			error = pm.page(dirname, name)
		if error: self.__error()

	def __from_data(self):
		page = form["page"].value.replace("/", os.sep)
		page = consts.DATA + os.sep + page
		if not os.path.isfile(page): self.__error()
		self.__make_page(page)

	def __incoming(self):
		file = form["file"].value
		files = lib.get_lines(consts.FILES, 0)
		if file not in files:
			self.__error("You do not have write-access to that file.")
		file = consts.FILES_DIR + os.sep + file
		handler = Incoming()
		error = handler.store(form, file)
		error and self.__error(error) or self.__from_data()

	def __blog(self, form):
		if "type" in form.keys():
			if form["type"].value == "ByTitle":
				from MingBlogServer import ByTitle
			elif form["type"].value == "ByCategory":
				from MingBlogServer import ByCategory
			if form["type"].value == "ByDate":
				from MingBlogServer import ByDate
		else:
			from MingBlogServer.LibBlog import *
			give_headers()
			dir = get_dir()
			author, email, title, tagline = get_text(dir)
			intro = get_lines(dir,"intro")
			footer = get_lines(dir,"footer")
			links = get_lines(dir,"links")
			content = content(dir, author, email)
			page = do_page(dir, title, tagline, intro, footer, links, content)
			print page
			sys.exit()

	def dynamic(self):
		if debug:
			import cgitb; cgitb.enable()
			print consts.HDR
			print "<h3>MAKING REPAIRS - NO PURCHASES</h3>"
		if "log" in form.keys():
			self.__log()
		elif "blog" in form.keys():
			self.__blog(form)
		elif "incoming" in form.keys():
			self.__incoming()
		elif "business" in form.keys(): # postpal
			self.__make_page("postpal")
		elif "type" in form.keys():	# prepal
			self.__make_page("prepal")
		elif "page" in form.keys():	# normal page
			self.__from_data()
		else:
			self.__error()

	#
	# Static methods
	#

	def __static_init(self):
		if debug:
			print "Params: " + `params`
			print "Options: " + `options`
		if len(params) != 2 or not os.path.isdir(params[0]):
			sys.exit(self.USAGE)

	def static(self):
		self.__static_init()
		one = params[0]
		two = params[1]
		if one[-1] == os.sep:
			one = one[:-1]
		if two[-1] == os.sep:
			two = two[:-1]
		s = SiteWalker()
		s.walk(one, two)

if __name__ == "__main__":
	ming = Ming()
	if form.keys():
		ming.dynamic()
	else:
		from TheMingServer import SiteWalker, params, options
		ming.static()
