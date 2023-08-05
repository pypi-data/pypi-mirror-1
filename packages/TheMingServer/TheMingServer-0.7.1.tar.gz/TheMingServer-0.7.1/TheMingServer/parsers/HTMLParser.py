
# HTMLParser.py
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


class HTMLParser:
	NAME = "HTMLParser"
	CONTENT = "content"
	TITLE = "title"
	DESC = "desc"

	def __init__(self, lib, debug):
		self.lib = lib
		self.debug = debug
		return

	def parse(self, title, desc, data):
		parsed_data = {
			self.TITLE:title,
			self.DESC:desc,
			}
		parsed_data = self.lib.parse_data(data, parsed_data)
		return parsed_data	
