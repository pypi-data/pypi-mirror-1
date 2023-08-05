
# HTMLMaker.py
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

import os, sys
from TheMingServer import lib

class HTMLMaker:
	NAME = "HTMLMaker"
	PLATE = "site.html"

	def __init__(self, source):
		self.source = source

	def make(self, parsed_data, plate=None):
		if plate == None: plate = self.source + os.sep + self.PLATE
		lines = lib.get_lines(plate)
		if lines == []:
			sys.exit(self.NAME + ": unable to read " + plate)
		page = lib.insert_tags(lines, parsed_data)
		return page
