
# PythonParser.py is part of The Ming Server
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

from TheMingServer import consts, lib, form, exceptions

class PythonParser:
	NAME = "PythonParser"
	CONTENT = "content"
	TITLE = "title"
	DESC = "desc"
	output = []

	def __init__(self):
		self.namespace = {"__builtins__": __builtins__,
						  "consts": consts,
						  "lib": lib,
						  "exceptions": exceptions}
		modules = ["os", "time", "sys"]
		for modname in modules:
			exec "import %s as mod" % modname
			self.namespace[modname] = mod

	def write(text):
		PythonParser.output.extend((text + "\n").splitlines(1))

	write = staticmethod(write)

	def exec_code(self, code):
		self.namespace["write"] = self.write
		self.namespace["params"] = ("params" in form.keys()) and form["params"].value or ""
		try: exec "\n".join(code) in self.namespace
		except  SystemExit, exit:
			if exit.code: raise

	def parse(self, title, desc, data):
		data = self.exec_code(data)
		parsed_data = {
			self.TITLE:title,
			self.DESC:desc,
			}
		parsed_data = lib.parse_data(self.output, parsed_data)
		return parsed_data