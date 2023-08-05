
# DirectSinglesPostPal.py is part of The Ming Mods
# billy-bob@billy-bob-ming.com

# Copyright (C) 2005, 2006  Richard Harris, Marco Rimoldi
# Released under the GNU General Public License
# (See the included COPYING file)

# The Ming Mods are free software; you can redistribute them and/or
# modify them under the terms of the GNU General Public License as published
# by the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# The Ming Mods are distributed in the hope that they will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with The Ming Mods; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import os
from TheMingServer import consts, lib, form

class DirectSinglesPostPal:
	NAME = "DirectSinglesPostPal"

	def __init__(self):
		pass

	def __parse_item(self, item):
		item = item.replace(" by ", "|")
		tokens = item.split("|")
		return tokens[0], tokens[1]

	def __get_path(self):
		item = form["item_name"].value
		name, author = self.__parse_item(item)
		lines = lib.get_subsite_file(name, "property_list", consts.DATA)
		for line in lines:
			if line.startswith(name):
				line = line.strip()
				path = line.split("=")[1]
				break
		return path

	def make_page(self):
		pre = 0
		path = self.__get_path()
		page = consts.DATA + os.sep + path
		lines = lib.get_lines(page)
		if lines[0].find(":pre") != -1:
			pre = 1
		lines = lines[6:]
		if pre:
			lines = ["<pre>"] + lines + ["</pre>"]
		return "\n".join(lines)