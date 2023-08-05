
# ErrorHandler.py is part of The Ming Server
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

import sys
from TheMingServer import lib, consts, form

class ErrorHandler:

	TEMPLATE = '''Content-Type: text/html

<?xml version="1.0" encoding="%(charset)s"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
  "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
  <head>
    <title> %(code)d - %(label)s </title>
  </head>
  <body>
    %(content)s
  </body>
</html>'''

	CONTENT = '''<h4> The Ming Server - %(label)s </h4>
    <p> %(message)s </p>
    <p> You may contact the <a href="mailto:%(contact)s">webmaster</a> to get support. %(query)s</p>'''

	def __init__(self):
		self.exceptions = Exceptions()
		sys.excepthook = self.catch_error

	def catch_error(type, instance, traceback):
		lib.prn(instance)
		if not issubclass(type, Exceptions.ServerError):
			instance = Exceptions.ServerError()
		classname = str(type).split(".")[-1]
		print instance.format_html()

	catch_error = staticmethod(catch_error)

class Exceptions:

	class ServerError(Exception):
		CODE = 500
		LABEL = "Internal Error"
		DEFAULT_MESS = "The Ming Server encountered an internal error or misconfiguration and was unable to complete your request."
		CONTACT = consts.EMAIL
		QUERY = '\n(It may be possible to reproduce this error using an <a href="%s">equivalent query</a> as well.)'

		def __init__(self, *args):
			#lib.prn(self.LABEL, "ERROR")
			if not args:
				args = (self.DEFAULT_MESS,)
			Exception.__init__(self, *args)

		def format_html(self):
			if "incoming" in form.keys():
				query = consts.SERVER + consts.CGI_NAME + "?"
				for key in form.keys():
					query += "%s=%s&amp;" % (key, form[key].value)
				query = self.QUERY % query
			else:
				query = ""
			keys = {'charset': consts.CHARSET,
					'content': ErrorHandler.CONTENT,
					'code': self.CODE,
					'label': self.LABEL,
					'message': self.args[0],
					'contact': self.CONTACT,
					'query': query}
			temp = ErrorHandler.TEMPLATE % keys
			return temp % keys

	class NotFoundError(ServerError):
		CODE = 404
		LABEL = "Resource Not Found"
		DEFAULT_MESS = "The page you requested could not be found."
		REDIRECT = '\n<p><a href="%s">Redirection</a> should begin shortly.</p>' % consts.SERVER

		def format_html(self):
			import os
			referer = os.environ.get("HTTP_REFERER", "")
			if consts.REDIRECT and not referer.startswith(consts.SERVER):
				ErrorHandler.TEMPLATE = consts.HDR_REDIRECT + "\n" + ErrorHandler.TEMPLATE
				ErrorHandler.CONTENT += self.REDIRECT
			return Exceptions.ServerError.format_html(self)

	class ForbiddenError(ServerError):
		CODE = 403
		LABEL = "Access Forbidden"
		DEFAULT_MESS = "You do not have permission to access this resource."

	class SubmissionError(ServerError):
		CODE = 409 # Conflict
		LABEL = "Duplicate Submission"
		DEFAULT_MESS = "Your submission cannot be accepted because it has already been processed."

#-------------------------------------------------------------------------
exceptions = ErrorHandler().exceptions