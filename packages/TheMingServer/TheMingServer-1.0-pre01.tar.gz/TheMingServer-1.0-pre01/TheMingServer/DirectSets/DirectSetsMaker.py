
# DirectSetsMaker.py is part of The Ming Mods
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
from TheMingServer.makers.HTMLMaker import HTMLMaker
from TheMingServer.DirectSets import PurchaseButton
from TheMingServer import consts, lib

class DirectSetsMaker(HTMLMaker):
	NAME = "DirectSetsMaker"
	BEGIN = ["""<h3>This is a sampling of the complete work.</h3>
	Number of pieces in complete set: """]
	END = ["<h4>End of Sample</h4>\n"]
	INNER_PLATE = os.path.dirname(__file__) + os.sep + "plate"

	def __init__(self, dirname):
		HTMLMaker.__init__(self, dirname)
		self.list = None
		self.table = None
		self.center = None

	def __parse_content(self, content):
		self.author = content[0].strip()
		self.fee = content[1].strip()
		self.email = content[2].strip()
		self.path = content[3].strip()
		# get properties in path
		files = os.listdir(consts.DATA + os.sep + self.path)
		files.remove("set.notes")
		files.remove("set.key")
		total = len(files)
		self.BEGIN = self.BEGIN + [`total`]
		content = content[4:]
		try:
			count = int(content[0].strip())
			files.sort()
			self.list = files[:count]
		except:
			self.list = []
			for line in content:
				line = line.strip()
				if line:
					self.list.append(line)

	def __preview_content(self):
		property = []
		notes = os.sep.join((consts.DATA, self.path, "set.notes"))
		if os.path.isfile(notes):
			property = lib.get_lines(notes)
			if property[0].find("<table") != -1:
				self.table = "</table>"
			if property[0].find("<center") != -1:
				self.center = "</center>"
		property.append("<h4>Author's Sample</h4>\n<ul>\n")
		lines = lib.get_lines(consts.DATA+os.sep+self.path+os.sep+"set.key")
		for entry in self.list:
			path = self.path + "/" + entry
			for i in range(0, len(lines)):
				if lines[i].startswith(entry):
					title = lines[i+1].strip()
					break
			property.append('<li><a href="%s?page=%s">%s</a>\n' \
							% (consts.CGI_NAME, path, title))
		property.append("</ul>\n")
		if self.table:
			property.append(self.table)
		if self.center:
			property.append(self.center)
		property = self.BEGIN + property + self.END
		return property

	def make(self, parsed_data):
		self.__parse_content(parsed_data["content"])
		del parsed_data["content"]
		parsed_data["property"] = self.__preview_content()
		p = PurchaseButton()
		parsed_data["button"] = p.button(parsed_data["title"], self.author, self.email, self.fee)
		content = lib.get_lines(self.INNER_PLATE)
		parsed_data["content"] = lib.insert_tags(content, parsed_data)
		page = HTMLMaker.make(self, parsed_data)
		return page
