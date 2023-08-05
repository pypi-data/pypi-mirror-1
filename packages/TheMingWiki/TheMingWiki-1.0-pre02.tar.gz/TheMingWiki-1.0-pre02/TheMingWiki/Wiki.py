
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

import cgi, sys, re
import cgitb; cgitb.enable()
from os import path, environ

import LibWiki, Page

class Wiki:

	INCOMING_MAX = 8*1024                  # max size allowed in incoming data
	word_re_str = r"\b([A-Z][a-z]+){2,}\b" #  defines WikiWord
	word_anchored_re = re.compile('^' + word_re_str + '$')

	def __init__(self, data, css, logo):
		self.data = data
		self.css = css
		self.logo = logo
		return

	#
	#  MAIN
	#

	def start(self):
		form = cgi.FieldStorage()
		print "Content-type: text/html\n"

		# tmp security
		remote_name = environ.get('REMOTE_ADDR', '')
		if (not (remote_name.find("63.229") == 0) and
			(not path.exists(path.expanduser("~/.my_machine")))):
			print '<h1>&nbsp;</h1>'
			print '<h3 align="center">403 -- Access Forbidden</h3>'
			print '<p align="center">You do not have permission to access this resource.'
			raise SystemExit
		# tmp security

		self.lib = LibWiki.LibWiki(self.data, self.logo, self.css, form, self.word_anchored_re)

		handlers = { 'fullsearch':	self._do_fullsearch,
					 'titlesearch': self._do_titlesearch,
					 'edit':		self._do_edit_1,
					 'access':      self._do_edit_2,
					 'savepage':	self._do_savepage }

		for cmd in handlers.keys():
			if form.has_key(cmd):
				if form.has_key('savetext'):
					apply(handlers[cmd], (form[cmd].value, form['savetext'].value,))
				elif form.has_key('access'):
					apply(handlers[cmd],
						  (form[cmd].value, form['name'].value, form['password'].value,))
				else:
					apply(handlers[cmd], (form[cmd].value,))
				break
		else:
			path_info = environ.get('PATH_INFO', '')

			if len(path_info) and path_info[0] == '/':
				query = path_info[1:] or 'FrontPage'
			else:		
				query = environ.get('QUERY_STRING', '') or 'FrontPage'

			word_match = re.match(self.word_re_str, query)
			if word_match:
				word = word_match.group(0)
				p = Page.Page(self.lib, word)
				p.send_page()
			else:
				print "<p>Can't work out query \"<pre>" + query + "</pre>\""

		sys.stdout.flush()

	#
	# Private Handlers
	#

	def _do_fullsearch(self, needle):
		self.lib.send_title('Full text search for "%s"' % (needle))
		needle_re = re.compile(needle, re.IGNORECASE)
		hits = []
		all_pages = self.lib.page_list()
		for page_name in all_pages:
			body = self.lib.read_body(page_name)
			count = len(needle_re.findall(body))
			if count:
				hits.append((count, page_name))

		# The default comparison for tuples compares elements in order,
		# so this sorts by number of hits
		hits.sort()
		hits.reverse()

		print "<UL>"
		for (count, page_name) in hits:
			print '<LI>' + self.lib.link_to(page_name)
			print ' . . . . ' + `count`
			print ['match', 'matches'][count <> 1]
		print "</UL>"
		self.lib.print_search_stats(len(hits), len(all_pages))

	def _do_titlesearch(self, needle):
		# XXX: check needle is legal -- probably can accept any RE
		self.lib.send_title("Title search for \"" + needle + '"')
		needle_re = re.compile(needle, re.IGNORECASE)
		all_pages = self.lib.page_list()
		hits = filter(needle_re.search, all_pages)
		print "<UL>"
		for filename in hits:
			print '<LI>' + self.lib.link_to(filename)
		print "</UL>"
		self.lib.print_search_stats(len(hits), len(all_pages))

	def _do_edit_1(self, pagename):
		if self.lib.is_public(pagename):
			self._do_edit(pagename)
		else:
			p = Page.Page(self.lib, pagename)
			p.send_authenticate()

	def _do_edit_2(self, pagename, usr, pwd):
		if self.lib.has_access(usr, pwd):
			self._do_edit(pagename)
		else:
			p = Page.Page(self.lib, pagename)
			str = "<b>You do not have edit access to this page.</b>"
			p.send_page(msg=str)
			
	def _do_edit(self, pagename):	
		p = Page.Page(self.lib, pagename)
		p.send_editor()

	def _do_savepage(self, pagename, saveval):
		pg = Page.Page(self.lib, pagename)
		if len(saveval) > self.INCOMING_MAX:
			str = """<b>Your edit exceeds the allowable size.</b>"""
		else:
			pg.save_text(saveval)
			str = """<b>Thank you for your changes.
			Your attention to detail is appreciated.</b>"""
		pg.send_page(msg=str)

