
# ArgParser.py
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

import sys, cgi
from os import sep

form = cgi.FieldStorage()
options, params = [], [] # command line stuff
if not form.keys():
	add = 0
	args = sys.argv
	for i in range(1, len(args)):
		arg = args[i]
		if arg.startswith('--'):
			if ":" in arg:
				add = 1
				arg = arg.replace(":", "")
			options.append(arg.replace("--" , ""))
		elif arg.startswith("-"):
			for j in range(1, len(arg)):
				options.append(arg[j])
		elif add:
			add = 0
			options.append(arg)
		elif arg:
			arg = arg.replace('/', sep)
			params.append(arg)
	debug = "debug" in options		
	force = "force" in options
else:			
	debug = "debug" in form.keys()
	force = 0
	
#debug = 1 # for postpal testing
