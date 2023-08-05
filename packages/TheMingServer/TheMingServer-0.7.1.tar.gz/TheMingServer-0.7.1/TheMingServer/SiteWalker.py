
# SiteWalker.py
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

import os, time
from PageMaker import PageMaker

class SiteWalker:
	NAME = "SiteWalker"
	
	def __init__(self, debug, lib, consts, force):
		self.debug = debug
		self.lib = lib
		self.consts = consts
		self.force = force

	def __make_stamp(self):
		now = time.time()
		f = open(self.stamp,'w')
		f.write(`now`)
		f.close()
		return

	def __get_stamp(self):
		if (self.force):
			return 0
		last_time = None
		if (os.path.exists(self.stamp)):
			f = open(self.stamp)
			last = float(f.readline().strip())
			f.close()
		else:
			return 0
		return last

	def __walk_it(self, arg, dirname, names):
		if (self.debug): print self.NAME+": "+dirname
		last = arg[2]
		# has the key been updated
		if not ("key" in names):
			return 1
		else:
			key = os.path.getmtime(dirname+os.sep+"key")
			if (key > last):
				update = 1
			else:
				update = 0
		pm = PageMaker(arg[0], arg[1], self.lib, self.consts, self.debug)
		for name in names:
			longname = dirname + os.sep + name
			mtime = os.path.getmtime(longname)
			if "~" not in name: # no backups
				if ((update) or 
					(mtime > last)):
					pm.page(dirname, name)

	def walk(self, one, two):
		self.dest = two
		self.stamp = self.dest + os.sep + "time.stamp"
		last = self.__get_stamp()
		os.path.walk(one, self.__walk_it, (one, two, last))
		self.__make_stamp()
