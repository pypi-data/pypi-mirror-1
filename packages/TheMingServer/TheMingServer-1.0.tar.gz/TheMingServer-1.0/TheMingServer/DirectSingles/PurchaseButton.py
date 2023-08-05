
# PurchaseButton.py is part of The Ming Mods
# billy-bob@billy-bob-ming.com

# Copyright (C) 2005, 2006  Richard Harris, Marco Rimoldi
# Released under the GNU General Public License
# (See the included COPYING file)

# The Ming Mods are free software; you can redistribute them and/or
# modify them under the terms of the GNU General Public License as published
# by the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# The Ming Mods are distributed in the hope that they will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with The Ming Mods; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

from TheMingServer import consts
class PurchaseButton:
	NAME = "PurchaseButton"

	def __init__(self):
		pass

	def button(self, property, author, email, fee):
		CGI_NAME = consts.CGI_NAME
		form = '''
		<form action="%s" method="get">
		<input type="hidden" name="property" value="%s">
		<input type="hidden" name="fee" value="%s">
		<input type="hidden" name="author" value="%s">
		<input type="hidden" name="email" value="%s">
		<input type="hidden" name="type" value="DirectSingles">
		<input type="submit"  name="submit" value="Read The Entire Work">
		</form>
		''' % (CGI_NAME, property, fee, author, email)
		return form