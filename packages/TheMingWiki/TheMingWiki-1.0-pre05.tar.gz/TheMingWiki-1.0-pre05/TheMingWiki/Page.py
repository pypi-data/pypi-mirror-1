
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

	def __init__(self, lib, PageName):
		self.pf = PageFormatter.PageFormatter(lib)
		self.PageName = PageName
		self.lib = lib

	#
	# Public Methods
	#

	def save_page(self, newtext):
		self.lib.save_page(self.PageName, newtext)

	def send_authenticate(self, msg=None):
		header = self.lib.gen_header('Access ' + self.PageName)

		print header
		print '''<h3>Edit Access Requires Authentication</h3>
<form>
<h4>Username</h4>
<p><input type="text" maxlength="128" name="name" size="48" value="">
<h4>Password</h4>
<p><input type="password" maxlength="128" name="password" size="48" value="">
<h4>Submit</h4>
<input type="hidden" name="access" value="%s">
<input type="submit" name="submit" value=" Submit ">
</form>
''' % (self.PageName)

	def send_page(self, msg=None):
		link = self.lib.get_scriptname() + '?fullsearch=' + self.PageName
		header = self.lib.gen_header(self.PageName, link, msg)
		body = self.lib.read_body(self.PageName)
		# print page
		print header
		self.pf.print_html(body)
		self.lib.print_footer(self.PageName, 1, self.lib.last_modified(self.PageName))

	def send_editor(self):
		header = self.lib.gen_header('Edit ' + self.PageName)
		# print page
		print header
		print '''<h3>Pages are limited to about three manuscript
		pages in size (8kb).</h3>'''
		print '<form method="post" action="%s">' % (self.lib.get_scriptname())
		print '<input type=hidden name="savepage" value="%s">' % (self.PageName)
		body = self.lib.read_body(self.PageName).replace('\r\n', '\n')
		print """<textarea wrap="virtual" name="savetext" rows="17"
				 cols="80">%s</textarea>""" % body
		print """<br><input type=submit value="Save">
				 <input type=reset value="Reset"><br></form>"""
		print "<p>" + self.lib.link_to('EditingTips')

	def send_fullsearch(self, hits, pages):
		# The default comparison for tuples compares elements in order,
		# so this sorts by number of hits
		hits.sort()
		hits.reverse()

		header = self.lib.gen_header('Full text search for "%s"' % (self.PageName))
		print header
		print "<UL>"
		for (count, PageName) in hits:
			print '<LI>' + self.lib.link_to(PageName)
			print ' . . . . ' + `count`
			print ['match', 'matches'][count <> 1]
		print "</UL>"
		self.lib.print_search_stats(len(hits), pages)

	def send_titlesearch(self, hits, pages):	
		header = self.lib.gen_header("Title search for \"" + self.PageName + '"')
		print header
		print "<UL>"
		for filename in hits:
			print '<LI>' + self.lib.link_to(filename)
		print "</UL>"
		self.lib.print_search_stats(len(hits), pages)


