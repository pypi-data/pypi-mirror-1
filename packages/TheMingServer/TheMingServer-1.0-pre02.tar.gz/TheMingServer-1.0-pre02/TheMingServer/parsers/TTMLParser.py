
# TTMLParser.py is part of The Ming Server
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

from HTMLParser import HTMLParser

class TTMLParser(HTMLParser):
	NAME = "TTMLParser"

	def __init__(self):
		HTMLParser.__init__(self)

	def __parse_3tml(self, lines):
		new_lines = ["<p>"]
		pre = block = list = 0
		for line in lines:
			if (line.find("<pre>") != -1) or (line.find("</pre>") != -1):
				pre = not pre
			if line.startswith("|"): # | for blockquote
				line = block and "</blockquote>" or "<blockquote>"
				block = not block
			elif line.startswith("+"): # | for blockquote
				line = list and "</ul>" or "<ul>"
				list = not list
			elif line.startswith("\\"):	# \ for <br>
				line = "<br />\n" + line[1:]
			elif line.startswith("!"): # ! for <h4>
				line = "<h4> %s </h4>" % line[1:]
			elif line.startswith("@"): # @ for href
				line = line[1:]
				href, title = line.count(" ") and line.split(" ", 1) or [line] * 2
				for i in range(len(title) - 1, -1, -1):
					if title[i] in ".,;:!?)]} ": continue
					i += 1
					leftout, title  = title[i:], title[:i]
					break
				line = '<a href="%s">%s</a>%s ' % (href, title, leftout)
			elif (line.strip() == "") and not pre:  # empty line for <p>
				line = "</p>\n<p>"
			if list and (line.find("ul>") == -1):
				line = "<li> %s </li>" % line

			new_lines.append(line)

		new_lines.append("</p>")
		return new_lines

	def parse(self, title, desc, data):
		data = self.__parse_3tml(data)
		parsed_data = HTMLParser.parse(self, title, desc, data)
		return parsed_data