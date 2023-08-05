
# Localizer.py is part of The Ming Server
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

import os
from TheMingServer import lib

lib.prn(__name__, "init")

class Localizer:

	def __init__(self):
		header = os.environ.get("HTTP_ACCEPT_LANGUAGE", "")
		self.user_prefs = [locale[:2] for locale in header.split(",")]

	def get_resource(self, resource, locales):
		locales = [entry.strip() for entry in locales.split(",")]
		for locale in self.user_prefs:
			if locale in locales:
				break
		else:
			locale = locales[0]
		lib.prn("using '%s' locale" % locale, "INFO")
		return lib.get_lines(resource + "." + locale)

#----------------------------------
localizer = Localizer()


