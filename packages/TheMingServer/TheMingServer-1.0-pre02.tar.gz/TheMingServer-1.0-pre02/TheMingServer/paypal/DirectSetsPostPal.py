
# DirectSetsPostPal.py is part of The Ming Mods
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

class DirectSetsPostPal:
	NAME = "DirectSetsPostPal"
	ORDER = "_order"

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
				tokens = line.split("=")
				path = tokens[1]
				method = tokens[2]
				break
		return path, method

	def __page(self, dir):
		page = []
		path = dir + os.sep + "set.notes"
		if os.path.exists(path):
			page = lib.get_lines(path)
		lines = lib.get_lines(dir + os.sep + "set.key")
		files = lib.parse_key(lines)
		keys = files.keys()
		keys.remove(self.ORDER)
		keys.sort()
		for key in keys:
			lines = lib.get_lines(dir + os.sep + key)
			pre = lines[0].find("pre") != -1
			title = "<h4>" + files[key][0] + "</h4>"
			lines = [title] + lines[1:]
			if pre: lines = ["<pre>"] + lines + ["</pre>"]
			page = page + lines
		return page

	def make_page(self):
		path, method = self.__get_path()
		dir = consts.DATA + os.sep + path
		if method == "page":			# allows for new methods (mp3, img, etc.)
			page = self.__page(dir)
		return "\n".join(page)
