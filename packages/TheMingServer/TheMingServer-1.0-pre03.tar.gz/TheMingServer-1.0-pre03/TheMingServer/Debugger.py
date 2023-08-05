
# Debugger.py is part of The Ming Server
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

from TheMingServer import debug, form, consts, lib
import sys, cStringIO, cgitb, atexit

class Debugger:

	SHOW_INFO = 4
	SHOW_TRACEBACK = 5
	FRAMESET = '''%s

<?xml version="1.0" encoding="%s"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Frameset//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-frameset.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
  <head>
    <title> The Ming Server Debug Framework </title>
  </head>
  <frameset rows="%s">
    %s
  </frameset>
</html> '''
	FRAME = '<frame src="%s?%%sdebug=%%d"/>\n' % consts.CGI_NAME

	def __init__(self):
		if debug > 3:
			self.output = cStringIO.StringIO()
			if debug == self.SHOW_INFO:
				lib.enable_printing(self.output)
			elif debug == self.SHOW_TRACEBACK:
				self.output.write(consts.HDR_CONTENT_TYPE + "\n\n" + "<h2>No errors were encountered while serving this page. Yippee!</h2>")
				self.output.seek(0)
				sys.excepthook = cgitb.Hook(file=self.output)
			else:
				return
			sys.stdout = cStringIO.StringIO() # just sends the normal output to mars
			atexit.register(self.onexit, self.output)
		else:
			frames = ""
			ratios = []
			query = ""
			for key in form.keys():
				if key != "debug":
					query += "%s=%s&amp;" % (key, form[key].value)
			if debug & 1:
				frames += self.FRAME % (query, self.SHOW_INFO)
				ratios.append("*")
			if debug & 2:
				frames += self.FRAME % (query, self.SHOW_TRACEBACK)
				ratios.append("2*")
			frames += self.FRAME % (query, 0)
			ratios.append("26%")
			print self.FRAMESET % (consts.HDR_CONTENT_TYPE, consts.CHARSET,
								   ",".join(ratios), frames)
			sys.exit()

	def onexit(output):
		sys.stdout = sys.__stdout__
		output.seek(0)
		print output.read()

	onexit = staticmethod(onexit)

#-------------------------------------------------------------------------
debugger = Debugger()