#!/usr/bin/python -u

# ming.cgi -- executable for The Ming Server
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

if os.path.exists("/home/richard/.my_machine"):
	SERVER = "http://192.168.56.2"
	SERVER = "http://63.229.144.206"
	# root of all your data files - can be read-only
	SITE_DIRECTORY = "../data"
	# incoming data handler's dir - must be read-write-execute
	FILES_DIR = "../files"
	# if you are using the MingBlogServer
	BLOGS_DIRECTORY = "../public_html/blogs"
else: # else handles chrooted virtual host accounts
	SERVER = "http://billy-bob-ming.com"
	# root of all your data files - can be read-only
	SITE_DIRECTORY = os.path.expanduser("~/data")
	# incoming data handler's dir - must be read-write-execute
	FILES_DIR = os.path.expanduser("~/files")
	# if you are using the MingBlogServer
	BLOGS_DIRECTORY = os.path.expanduser("~/public_html/blogs")

LOG_DIR = FILES_DIR

#========================================

from TheMingServer import Ming
server = Ming()
server.start()
