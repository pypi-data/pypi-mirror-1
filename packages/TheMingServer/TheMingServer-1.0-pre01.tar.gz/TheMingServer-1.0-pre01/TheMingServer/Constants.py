
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
	HDR_REDIRECT = ""
	SERVER = SERVER
	CGI_NAME = os.environ["SCRIPT_NAME"]
	DATA = expand(SITE_DIRECTORY)
	FILES_DIR = expand(FILES_DIR)
	LOG_DIR = expand(LOG_DIR)
	FILES = FILES_DIR + os.sep + "ming.files"

	# SITE OPTIONS
	def __init__(self):
		# put any default value here
		user_consts = {"CHARSET": "iso-8859-1",
					   "REDIRECT_URL": "/",
					   "REDIRECT_TIME": 4}

		# read options set by user
		try:
			path = os.path.join(self.DATA, "consts")
			consts = open(path)
		except:
			raise ConstantError, 'could not open the constants file %s' % path

		# fill user_consts with anything defined in consts
		exec consts in globals(), user_consts

		# make that "anything" accessible from self
		for const, value in user_consts.items():
			if isinstance(value, str):
				value = expand(value)
			setattr(self, const, value)

		# derived constants
		self.HDR_CONTENT_TYPE = "Content-Type: text/html; charset=" + self.CHARSET
		self.HDR_REDIRECT = "Refresh: %s; URL=%s" % (self.REDIRECT_TIME, self.REDIRECT_URL)

	def __getattr__(self, name):
		try:
			return self.__dict__[name]
		except:
			raise ConstantError, 'cannot find constant "%s"' % name

#-------------------------------------------------------------------------
consts = Constants()