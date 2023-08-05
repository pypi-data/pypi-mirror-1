
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

	word_re_str = r"\b([A-Z][a-z]+){2,}\b" #  defines WikiWord
	word_anchored_re = re.compile('^' + word_re_str + '$')

	def __init__(self, data, css, logo):
		self.css = css
		self.logo = logo
		self.text_dir = path.join(data, 'text')
		self.edit_log = path.join(data, 'editlog')
		return

	#
	# Handlers
	#

	def do_fullsearch(self, needle):
		self.lib.send_title('Full text search for "%s"' % (needle))
		needle_re = re.compile(needle, re.IGNORECASE)
		hits = []
		all_pages = self.lib.page_list()
		for page_name in all_pages:
			p = Page.Page(self.lib, self.text_dir, page_name)
			body = p.get_raw_body()
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


	def do_titlesearch(self, needle):
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

	def do_edit(self, pagename):
		p = Page.Page(self.lib, self.text_dir, pagename)
		p.send_editor()

	def do_savepage(self, pagename, saveval):
		pg = Page.Page(self.lib, self.text_dir, pagename)
		pg.save_text(saveval)
		msg = """<b>Thank you for your changes.
		Your attention to detail is appreciated.</b>"""
		pg.send_page(msg=msg)


	#
	#  MAIN
	#

	def start(self):
		form = cgi.FieldStorage()
		print "Content-type: text/html\n"

		self.lib = LibWiki.LibWiki(self.text_dir, self.logo, self.edit_log,
							  self.css, form, self.word_anchored_re)

		handlers = { 'fullsearch':	self.do_fullsearch,
					 'titlesearch': self.do_titlesearch,
					 'edit':		self.do_edit,
					 'savepage':	self.do_savepage }

		for cmd in handlers.keys():
			if form.has_key(cmd):
				if form.has_key('savetext'):
					apply(handlers[cmd], (form[cmd].value, form['savetext'].value,))
				else:
					apply(handlers[cmd], (form[cmd].value,))
				break
		else:
			path_info = environ.get('PATH_INFO', '')

			if form.has_key('goto'):
				query = form['goto'].value
			elif len(path_info) and path_info[0] == '/':
				query = path_info[1:] or 'FrontPage'
			else:		
				query = environ.get('QUERY_STRING', '') or 'FrontPage'

			word_match = re.match(self.word_re_str, query)
			if word_match:
				word = word_match.group(0)
				p = Page.Page(self.lib, self.text_dir, word)
				p.send_page()
			else:
				print "<p>Can't work out query \"<pre>" + query + "</pre>\""

		sys.stdout.flush()
