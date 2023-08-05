
# Constants.py
# billy_bob_ming@yahoo.com

# Copyright (C) 2005 by Richard Harris
# Released under the GNU General Public License
# (See the included COPYING file)

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.

# You should have received a copy of the GNU General Public License
# with this program; if not, write to the Free Software Foundation,
# Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

import os

class Constants:

	# USER CONSTANTS

	# PLATFORM INDEPENDENT CONSTANTS
	EMAIL = "billy_bob_ming@yahoo.com"							  # site's email account
	CGI_NAME = "ming.cgi"										  # CGI file's name (in case server is picky)
	#SERVER = "http://localhost/cgibin/%s" % CGI_NAME			  # CGI url (used in PrePal.py)
	SERVER = "http://billy-bob-ming.com/cgibin/%s" % CGI_NAME	  # CGI url (used in PrePal.py)
	FILE_MAX = 512*1024											  # max size of file in FILES_DIR
	INCOMING_MAX = 64*1024										  # max size allowed in incoming data
	PLATES = 1													  # 0 if only one site.html, else 1 (0 is faster)
	LOGGING = 0													  # on is 1, off is 0
	DEMO = 1													  # 1 makes log public
	LOG_PASSWD = "your_passwd_here"								  # Log passwd, used to reset log
	PRIVATE = "private"											  # dir trees hidden from log
	# E-ZINE CONSTANTS
	TITHE = 1				  # 1 activates tithing system
	USE_SPAN = 0			  # require transaction to occur within a limited period
	SPAN = 15				  # limited period in minutes

	#PLATFORM SWITCH
	IS_WIN32 = 0			  # 0 for Unix (Mac is BSD Unix now.) 1 for Windows (tm)

	if (IS_WIN32):
		DATA = "..\\data"					 # root of all your data files - can be read-only
		FILES_DIR = "..\\data\\files"		 # incoming data handler's dir - must be read-write
		LOG_DIR = FILES_DIR					 # where your log will be written - "." for cgi-bin
	else:
		if os.path.exists(os.path.expanduser("~/.my_machine")):
			DATA = "../data"					 # root of all your data files - can be read-only
			FILES_DIR = "../data/files"			 # incoming data handler's dir - must be read-write-execute
		else:	
			DATA =  os.path.expanduser("~/data") # root of all your data files - can be read-only
			FILES_DIR = os.path.expanduser("~/data/files") # incoming data handler's dir - must be read-write-execute
		LOG_DIR = FILES_DIR					 # where your log will be written - "." for cgi-bin

	# DERIVED CONSTANTS
	FILES = FILES_DIR+os.sep+"ming.files"	 # must be read/write on server


	# INTERNAL CONSTANTS -- DO NOT CHANGE
	HDR = "Content-Type: text/html\n\n"
	ID = "<h4>The Ming Server</h4>"
	E403 = "<h4>Error 403: Forbidden</h4>"
	E404 = "<h4>Error 404: Resource Not Found</h4>"
