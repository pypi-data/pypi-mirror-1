
# Wiki -- a part of The Ming Wiki

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

import cgi, re
from os import environ
# To stop python's debug pages,
# comment out next line
import cgitb; cgitb.enable()

import LibWiki, Page

class Wiki:

	INCOMING_MAX = 8*1024                  # max size allowed in incoming data
	word_re_str = r"\b([A-Z][a-z]+){2,}\b" #  defines WikiWord

	def __init__(self, data, css, logo, index=None):
		self.form = cgi.FieldStorage()
		self.lib = LibWiki.LibWiki(data, logo, css, self.form, self.word_re_str)
		if index:
			self.INDEX = index
		else:
			self.INDEX = 'FrontPage'
		return

	#
	#  MAIN
	#

	def start(self):
		# parse for handling
		handlers = { 'fullsearch':	self._do_fullsearch,
					 'titlesearch': self._do_titlesearch,
					 'edit':		self._do_edit_1,
					 'access':      self._do_edit_2,
					 'savepage':	self._do_savepage }

		for cmd in handlers.keys():
			if self.form.has_key(cmd):
				if self.form.has_key('savetext'):
					apply(handlers[cmd], (self.form[cmd].value, self.form['savetext'].value,))
				elif self.form.has_key('access'):
					apply(handlers[cmd], (self.form[cmd].value, self.form['name'].value,
										  self.form['password'].value,))
				else:
					apply(handlers[cmd], (self.form[cmd].value,))
				break
		else:
			path_info = environ.get('PATH_INFO', '')

			if len(path_info) and path_info[0] == '/':
				query = path_info[1:] or self.INDEX
			else:		
				query = environ.get('QUERY_STRING', '') or self.INDEX

			word_match = re.match(self.word_re_str, query)
			if word_match:
				word = word_match.group(0)
				p = Page.Page(self.lib, word)
				p.send_page()
			else:
				p = Page.Page(self.lib, query)
				p.send_error("Cannot match query: <pre>" + query + "</pre>")

	#
	# Private Methods
	#

	def _do_edit(self, PageName):	
		p = Page.Page(self.lib, PageName)
		p.send_editor()


	# Handlers

	def _do_fullsearch(self, needle):
		needle_re = re.compile(needle, re.IGNORECASE)
		hits = []
		all_pages = self.lib.page_list()
		pages = len(all_pages)
		for PageName in all_pages:
			body = self.lib.read_body(PageName)
			count = len(needle_re.findall(body))
			if count:
				hits.append((count, PageName))
		p = Page.Page(self.lib, needle)
		p.send_fullsearch(hits, pages)

	def _do_titlesearch(self, needle):
		# XXX: check needle is legal -- probably can accept any RE
		needle_re = re.compile(needle, re.IGNORECASE)
		all_pages = self.lib.page_list()
		pages = len(all_pages)
		hits = filter(needle_re.search, all_pages)
		p = Page.Page(self.lib, needle)
		p.send_titlesearch(hits, pages)

	def _do_edit_1(self, PageName):
		if self.lib.is_public(PageName):
			self._do_edit(PageName)
		else:
			p = Page.Page(self.lib, PageName)
			p.send_authenticate()

	def _do_edit_2(self, PageName, usr, pwd):
		if self.lib.has_access(usr, pwd):
			self._do_edit(PageName)
		else:
			p = Page.Page(self.lib, PageName)
			str = "<b>You do not have edit access to this page.</b>"
			p.send_page(msg=str)
			
	def _do_savepage(self, PageName, saveval):
		p = Page.Page(self.lib, PageName)
		if len(saveval) > self.INCOMING_MAX:
			str = """<b>Your edit exceeds the allowable size.</b>"""
		else:
			p.save_page(saveval)
			str = """<b>Thank you for your changes.
			Your attention to detail is appreciated.</b>"""
		p.send_page(msg=str)
