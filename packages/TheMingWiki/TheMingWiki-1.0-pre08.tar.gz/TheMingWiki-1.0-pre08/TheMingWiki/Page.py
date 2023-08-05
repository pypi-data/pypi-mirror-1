
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

import sys, string, re
from os import environ

import PageFormatter

class Page:

	def __init__(self, lib, PageName):
		self.pf = PageFormatter.PageFormatter(lib)
		self.PageName = PageName
		self.lib = lib
		self.has_plate = self.lib.plate

	#
	# Public Methods
	#

	def save_page(self, newtext):
		self.lib.save_page(self.PageName, newtext)

	def send_authenticate(self):
		# header
		if self.has_plate:
			header = 'Access ' + self.PageName
		else:	
			header = self._gen_header('Access ' + self.PageName)
		# body
		body = '''<h3>Edit Access Requires Authentication</h3>
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
		self._write_page(header, body)

	def send_page(self, msg=""):
		link = self.lib.get_scriptname() + '?fullsearch=' + self.PageName
		# header
		if self.has_plate:
			header = self.PageName
		else:	
			header = self._gen_header(self.PageName, link, msg)
		# body
		body = self.lib.read_body(self.PageName)
		body = self.pf.format_page(body)
		body = msg + body
		# footer
		modified = self.lib.last_modified(self.PageName)
		footer = self._gen_footer(self.PageName, 1, modified)
		self._write_page(header, body, footer)

	def send_editor(self):
		areatext = self.lib.read_body(self.PageName).replace('\r\n', '\n')
		# header
		if self.has_plate:
			header = 'Edit ' + self.PageName
		else:	
			header = self._gen_header('Edit ' + self.PageName)
		# body
		body = '''<h3>Pages are limited to about three pages in size (8kb).</h3>'''
		body += '<form method="post" action="%s">' % (self.lib.get_scriptname())
		body += '<input type=hidden name="savepage" value="%s">' % (self.PageName)
		body += """<textarea wrap="virtual" name="savetext" rows="17"
				 cols="80">%s</textarea>""" % areatext
		body += """<br><input type=submit value="Save">
				 <input type=reset value="Reset"><br></form>"""
		body += "<p>" + self.lib.link_to('EditingTips')
		self._write_page(header, body)

	def send_error(self, msg):
		header = "<h3>Error</h3>"
		body = msg
		self._write_page(header, body)

	def send_fullsearch(self, hits, pages):
		# header
		if self.has_plate:
			header = 'Full text search for "%s"' % (self.PageName)
		else:
			header = self._gen_header('Full text search for "%s"' % (self.PageName))
		# body
		if len(hits) == 0:
			body = "No Matches Found"
		else:
			hits.sort()
			hits.reverse()
			body = "<ul>"
			total = 0
			for (count, PageName) in hits:
				body += '<li>' + self.lib.link_to(PageName)
				body += ' . . . . ' + `count`
				body += [' match', ' matches'][count <> 1]
				total += count
			body += "</ul>"
			body += self._search_stats(total, pages)
		# footer
		footer = self._gen_footer(self.PageName, 0)
		self._write_page(header, body, footer)

	def send_titlesearch(self, hits, pages):
		# header
		if self.has_plate:
			header = "Title search for \"" + self.PageName + '"'
		else:
			header = self._gen_header("Title search for \"" + self.PageName + '"')
		# body
		if len(hits) == 0:
			body = "No Matches Found"
		else:
			hits.sort()
			body = "<ul>"
			for filename in hits:
				body += '<li>' + self.lib.link_to(filename)
			body += "</ul>"
			body += "</ul>"
			body += self._search_stats(len(hits), pages)
		# footer
		footer = self._gen_footer(self.PageName, 0)
		self._write_page(header, body, footer)

	#
	# Private Methods
	#

	def _gen_header(self, text, link=None, msg=None):
		header = "<head><title>%s</title>" % text
		if self.lib.css_url:
			header += '<link rel="stylesheet" type="text/css" href="%s">' % self.lib.css_url
		header += '''</head>
		<body>
		<center>
		<table width="95%"><tr><td>
		<h1>'''
		if self.lib.logo_string:
			header += self.lib.logo_string
		if link:
			header += '<a href="%s">%s</a>' % (link, text)
		else:
			header += text
		header += '</h1>'
		if msg: header += msg
		header += '<hr>'
		return header

	def _gen_footer(self, name, editable=1, mod_string=None):
		footer = ""
		if not self.has_plate:
			footer += '<hr>'
		if editable:
			footer += self.lib.link_tag('?edit='+name, 'EditText')
			footer += " of this page "
			if mod_string:
				footer += " (last modified %s) " % mod_string
			footer += '<br>'
		footer += self.lib.link_tag('FindPage?value='+name, 'FindPage')
		footer += " by browsing, searching, or an index "
		footer += "</table>"
		return footer

	def _search_stats(self, hits, searched):
		stats = "<h5>%d matches out of %d pages searched.</h5>" % (hits, searched)
		return stats
	
	def _write_page(self, header="", body="", footer=""):
		print "Content-type: text/html\n"
		if self.has_plate:
			title = self.PageName
			wikiword = '''<h1>
			<a href="/cgibin/billiwik.cgi?fullsearch=%s">%s</a>
			</h1>''' % (title, title)
			lines = self.lib.lines_plate()
			for line in lines:
				print line
				if line.find("<!--title-->") != -1:
					print title
				elif line.find("<!--wikiword-->") != -1:
					print wikiword
				elif line.find("<!--content-->") != -1:
					print body
				elif line.find("<!--wikifooter-->") != -1:
					print footer
		else:
			print header
			print body
			print footer
		sys.stdout.flush()		
		
