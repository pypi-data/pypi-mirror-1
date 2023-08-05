
# PREParser.py is part of The Ming Server
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

from TheMingServer import lib
from PlainParser import PlainParser

class PREParser(PlainParser):
	NAME = "PREParser"
	CONTENT = "content"
	TITLE = "title"
	DESC = "desc"

	def __init__(self):
		PlainParser.__init__(self)

	def __parse(self, parsed_data):
		data = parsed_data[self.CONTENT]
		del parsed_data[self.CONTENT]
		pre = 1
		parsed_data = lib.parse_data(data, parsed_data, pre)
		return parsed_data

	def parse(self, title, desc, data):
		parsed_data = PlainParser.parse(self, title, desc, data)
		parsed_data = self.__parse(parsed_data)
		return parsed_data