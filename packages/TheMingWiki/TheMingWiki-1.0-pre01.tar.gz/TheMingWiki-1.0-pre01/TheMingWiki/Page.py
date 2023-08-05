
# Page -- a part of The Ming Wiki

# Copyright (C) 2006 Billy-Bob Ming
# billy-bob@billy-bob-ming.com
# Released under the GNU General Public License
# (See the included COPYING file)

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the GNU
# General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
# USA

# Hack History
# Copyright (C) 1999, 2000 Martin Pool <mbp@humbug.org.au> - piki

import string, re
from os import environ

import PageFormatter

class Page:

	def __init__(self, lib, page_name):
		self.pf = PageFormatter.PageFormatter(lib)
		self.page_name = page_name
		self.lib = lib

	#
	# Public Methods
	#

	def send_page(self, msg=None):
		link = self.lib.get_scriptname() + '?fullsearch=' + self.page_name
		self.lib.send_title(self._split_title(), link, msg)
		body = self.lib.read_body(self.page_name)
		self.pf.print_html(body)
		self.lib.print_footer(self.page_name, 1, self.lib.last_modified(self.page_name))

	def send_editor(self):
		self.lib.send_title('Edit ' + self._split_title())
		print '<form method="post" action="%s">' % (self.lib.get_scriptname())
		print '<input type=hidden name="savepage" value="%s">' % (self.page_name)
		body = self.lib.read_body(self.page_name).replace('\r\n', '\n')
		print """<textarea wrap="virtual" name="savetext" rows="17"
				 cols="80">%s</textarea>""" % body
		print """<br><input type=submit value="Save">
				 <input type=reset value="Reset"><br></form>"""
		print "<p>" + self.lib.link_to('EditingTips')

	def save_text(self, newtext):
		self.lib.write_file(self.page_name, newtext)
		remote_name = environ.get('REMOTE_ADDR', '')
		self.lib.editlog_add(self.page_name, remote_name)

	#
	# Private Methods
	#

	def _split_title(self):
		return re.sub('([a-z])([A-Z])', r'\1 \2', self.page_name)
