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

import cgi, os, sys, time
from TheMingServer import *

class ming:
	NAME = "ming"
	USAGE = '''
usage: '''+NAME+''' local/dir/one local/dir/two
'''

	def __init__(self):
		self.debug = 0
		self.consts = Constants()
		self.HDR = self.consts.HDR
		self.ID = self.consts.ID
		self.E404 = self.consts.E404
		self.lib = Lib3.Lib3(self.debug)
		self.DATA = self.consts.DATA
		self.FILES_DIR = self.consts.FILES_DIR
		self.FILES = self.consts.FILES
		if not (os.path.exists(self.FILES_DIR)):
			os.makedirs(self.FILES_DIR)
			os.chmod(self.FILES_DIR, 0777)
		return
	#
	# Dynamic methods
	#

	def __error(self, msg=None):
		print self.HDR+self.ID
		if (msg == None):
			print self.E404
		else:
			print "<h4>Error</h4>"
			print "<p>"+msg
		sys.exit()

	def __log(self, form):
		l = Logger(self.consts, self.debug)
		l.run(form)
		return

	def __make_page(self, form, page):
		pm = PageMaker(self.DATA, None, self.lib, self.consts, self.debug, form)
		if (page == "prepal"):
			error = pm.prepal()
		elif (page == "postpal"):
			error = pm.postpal()
		else:
			dirname, name = os.path.split(page)
			error = pm.page(dirname, name)
		if (error): self.__error()
		return

	def __from_data(self, form):
		page = form["page"].value.replace("/", os.sep)
		page = self.DATA+os.sep+page
		if not (os.path.isfile(page)): self.__error()
		self.__make_page(form, page)
		return

	def __incoming(self, form):
		file = form["file"].value
		files = self.lib.get_lines(self.FILES, 0)
		if (file not in files):
			self.__error("You do not have write-access to that file.")
		file = self.FILES_DIR+os.sep+file
		handler = Incoming(self.lib, self.consts, self.debug)
		error = handler.store(form, file)
		error and self.__error(error) or self.__from_data(form)
		return

	def __dynamic(self, form):
		if ("debug" in form.keys()): self.debug = 1
		#self.debug = 1
		if (self.debug):
			import cgitb; cgitb.enable()
			print self.HDR
		if ("log" in form.keys()):
			self.__log(form)
		elif ("incoming" in form.keys()):
			self.__incoming(form)
		elif ("business" in form.keys()): # postpal
			self.__make_page(form, "postpal")
		elif ("type" in form.keys()):	# prepal
			self.__make_page(form, "prepal")
		elif ("page" in form.keys()):	# normal page
			self.__from_data(form)
		else:
			self.__error()
		return

	#
	# Static methods
	#

	def __static_init(self):
		self.params = []
		self.options = []
		add = 0
		args = sys.argv
		for i in range(1, len(args)):
			arg = args[i]
			if (arg.find("--") == 0):
				if (":" in arg):
					add = 1
					arg = arg.replace(":", "")
				self.options.append(arg.replace("--", ""))
			elif (arg.find("-") == 0):
				for j in range(1,len(arg)):
					self.options.append(arg[j])
			elif (add):
				add = 0
				self.options.append(arg)
			elif (arg != ''):
				self.params.append(arg)
		self.debug = ("debug" in self.options)
		self.force = ("force" in self.options)
		if (self.debug):
			print "Params: "+`self.params`
			print "Options: "+`self.options`
		if ((len(self.params) != 2) or
			(not os.path.isdir(self.params[0]))):
			sys.exit(self.USAGE)
		return

	def __static(self):
		self.__static_init()
		one = self.params[0]
		two = self.params[1]
		if (one[-1] == os.sep):
			one = one[:-1]
		if (two[-1] == os.sep):
			two = two[:-1]
		s = SiteWalker(self.debug, self.lib, self.consts, self.force)
		s.walk(one, two)
		return

	def run(self):
		form = cgi.FieldStorage()
		if (form.keys() != []):
			self.__dynamic(form)
		else:
			self.__static()
		return

if __name__ == "__main__":
	obj = ming()
	obj.run()
