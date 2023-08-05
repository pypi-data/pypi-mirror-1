
# 3TMLParser.py
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

from HTMLParser import HTMLParser

class TTMLParser(HTMLParser):
	NAME = "TTMLParser"

	def __init__(self, lib, debug):
		HTMLParser.__init__(self, lib, debug)
		self.lib = lib
		self.debug = debug
		return

	def __parse_3tml(self, lines):
		new_lines = []
		pre = 0
		block = 0
		list = 0
		for line in lines:
			if "<pre>" in line:
				pre = 1
			elif "</pre>" in line:
				pre = 0
			if line.startswith("|"): # | for blockquote
				if not block:
					line = "<blockquote>\n"
					block = 1
				else:
					line = "</blockquote>\n"
					block = 0
			elif line.startswith("+"): # | for blockquote
				if not list:
					line = "<ul>\n"
					list = 1
				else:
					line = "</ul>\n"
					list = 0
			elif line.startswith("\\"):	# \ for <br>
				line = line.replace("\\", "", 1)
				line = "<br>" + line
			elif line.startswith("!"): # ! for <h4>
				line = line.replace("!", "", 1)
				line = "<h4>" + line + "</h4>"
			elif line.startswith("@"): # @ for href
				line = line.lstrip("@ ").rstrip(" \r\n")
				href, title = line.count(" ") and line.split(" ", 1) \
											  or [line] * 2
				leftout = ""
				while title[-1] in ".,;:!?)]} ":
					leftout = title[-1] + leftout
					title = title[:-1]
				line = '<a href="%s">%s</a>%s ' % (href, title, leftout)
			elif (line.strip() == "") and not pre:            # empty line for <p>
				line = "<p>\n"
			if (list) and ("ul>\n" not in line):
				line = "<li>"+line
			new_lines.append(line)
		new_lines.append("\n")
		return new_lines

	def parse(self, title, desc, data):
		data = self.__parse_3tml(data)
		parsed_data = HTMLParser.parse(self, title, desc, data)
		return parsed_data
