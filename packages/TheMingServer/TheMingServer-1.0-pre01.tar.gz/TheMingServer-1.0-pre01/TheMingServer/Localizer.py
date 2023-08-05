
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
from TheMingServer import lib, exceptions

lib.prn(__name__, "init")

class Localizer:

	def __init__(self):
		header = os.environ.get("HTTP_ACCEPT_LANGUAGE", "")
		prefs = header.split(',') # ["en", " es;q=0.8"]
		self.user_locales = [pref.split(';')[0].strip() for pref in prefs]

	def parse_header(self, line):
		header = line.strip()
		tokens = lib.tokens(header, ":")
		try:
			if tokens[0] == "locales":
				locales = lib.tokens(tokens[1], ",")
				return locales
		except:
			return None
		return None

	def get_resource(self, resource, available_locales):

		def pick_from(candidates):
			for locale in candidates:
				if locale in available_locales:
					path = resource + "." + locale
					if os.path.isfile(path):
						lib.prn("using '%s' locale" % locale, "INFO")
						return path
					else:
						lib.prn("%s does not exist!" % path, "WARNING")
						available_locales.remove(locale)

		path = pick_from(self.user_locales) or pick_from(tuple(available_locales))
		if not path:
			lib.prn("the requested page has not been localized!", "ERROR")
			raise exceptions.NotFoundError
		else:
			return path

#----------------------------------
localizer = Localizer()
