
# DirectSinglesMaker.py is part of The Ming Mods
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

from TheMingServer.makers.HTMLMaker import HTMLMaker
from TheMingServer.DirectSingles import PurchaseButton
from TheMingServer import lib
import os

class DirectSinglesMaker(HTMLMaker):
	NAME = "DirectSinglesMaker"
	BEGIN = ["<h3>This is a preview of the complete work.</h3>\n"]
	END = ["<h3>End of Preview</h3>\n"]
	INNER_PLATE = os.path.dirname(__file__) + os.sep + "plate"

	def __parse_content(self, content):
		pre = 0
		if content[0].find("<pre>") != -1:
			pre = 1
		author = content[1+pre].strip()
		author = lib.strip_html(author)
		return content, author

	def __find(self, list, char):
		list = ["null"] + list
		for item in list:
			if char in item:
				return item.strip()
		return None

	def __preview_content(self, content):
		length = len(content)
		if (length < 1000):
			content = content[:int(length/3.0)]
		else:
			content = content[:200]
		content, author = self.__parse_content(content)
		if content[0].startswith("<pre>"):
			content = content + ["\n</pre>\n"]
		content = self.BEGIN + content + self.END
		return content, author

	def make(self, parsed_data):
		parsed_data["content"], author = self.__preview_content(parsed_data["content"])
		p = PurchaseButton()
		email = self.__find(parsed_data["email"],"@")
		fee = self.__find(parsed_data["price"],".")
		parsed_data["button"] = p.button(parsed_data["title"], author, email, fee)
		content = lib.get_lines(self.INNER_PLATE)
		parsed_data["property"] = parsed_data["content"]
		del parsed_data["content"]
		parsed_data["content"] = lib.insert_tags(content, parsed_data)
		page = HTMLMaker.make(self, parsed_data)
		return page
