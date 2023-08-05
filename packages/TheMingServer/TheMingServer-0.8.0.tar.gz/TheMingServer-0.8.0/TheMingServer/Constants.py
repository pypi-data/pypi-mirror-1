
# Constants.py is part of The Ming Server
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
from __main__ import SERVER, SITE_DIRECTORY, FILES_DIR, LOG_DIR

expand = lambda arg: os.path.expanduser(os.path.expandvars(arg))

class ConstantError(AttributeError):
	pass

class Constants:

	# INTERNAL CONSTANTS
	HDR_CONTENT = "Content-Type: text/html"
	HDR_REDIRECT = "Refresh: 4; URL=/"
	SERVER = SERVER
	CGI_NAME = os.environ["SCRIPT_NAME"]
	DATA = expand(SITE_DIRECTORY)
	FILES_DIR = expand(FILES_DIR)
	LOG_DIR = expand(LOG_DIR)
	FILES = FILES_DIR + os.sep + "ming.files"

	# SITE OPTIONS
	def __init__(self):
		user_consts = {} # we could put some default values here
		try:
			path = os.path.join(self.DATA, "consts")
			consts = open(path)
		except:
			raise ConstantError, 'could not open the constants file %s' % path
		exec consts in globals(), user_consts
		for const, value in user_consts.items():
			if isinstance(value, str):
				value = expand(value)
			setattr(self, const, value)

	def __getattr__(self, name):
		try:
			return self.__dict__[name]
		except:
			raise ConstantError, 'cannot find constant "%s"' % name

#-------------------------------------------------------------------------
consts = Constants()