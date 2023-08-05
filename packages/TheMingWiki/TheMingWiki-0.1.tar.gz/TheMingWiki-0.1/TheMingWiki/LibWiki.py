
# LibWiki -- a part of The Ming Wiki

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

import string, time, os
from os import path, environ

class LibWiki:

	nonexist_qm = 0	# show '?' for nonexistent?

	def __init__(self, text_dir, logo, editlog_name, css_url, form, word_anchored_re):
		self.text_dir = text_dir
		self.logo_string = logo
		self.editlog_name = editlog_name
		self.css_url = css_url
		self.form = form
		self.word_anchored_re = word_anchored_re
		return

	def editlog_add(self, page_name, host):
		editlog = open(self.editlog_name, 'a+')
		try: 
			editlog.seek(0, 2)	# to end
			editlog.write(string.join((page_name, host, `time.time()`), "\t") + "\n")
		finally:
			editlog.close()

	def editlog_raw_lines(self):
		editlog = open(self.editlog_name, 'rt')
		try:
			return editlog.readlines()
		finally:
			editlog.close()

	def get_scriptname(self):
		return environ.get('SCRIPT_NAME', '')

	def send_title(self, text, link=None, msg=None):
		print "<head><title>%s</title>" % text
		if self.css_url:
			print '<link rel="stylesheet" type="text/css" href="%s">' % self.css_url
		print "</head>"
		print '<body><h1>'
		if self.logo_string:
			print self.link_tag('RecentChanges', self.logo_string)
		if link:
			print '<a href="%s">%s</a>' % (link, text)
		else:
			print text
		print '</h1>'
		if msg: print msg
		print '<hr>'

	def link_tag(self, params, text=None, ss_class=None):
		if text is None:
			text = params					# default
		if ss_class:
			classattr = 'class="%s" ' % ss_class
		else:
			classattr = ''
		return '<a %s href="%s/%s">%s</a>' % \
			   (classattr, self.get_scriptname(), params, text)

	def print_footer(self, name, editable=1, mod_string=None):
		base = self.get_scriptname()
		print '<hr>'
		if editable:
			print self.link_tag('?edit='+name, 'EditText')
			print "of this page"
			if mod_string:
				print "(last modified %s)" % mod_string
			print '<br>'
		print self.link_tag('FindPage?value='+name, 'FindPage')
		print " by browsing, searching, or an index"


	def link_to(self, page_name):
		if path.exists(path.join(self.text_dir, page_name)):
			return self.link_tag(page_name)
		else:
			if self.nonexist_qm:
				return self.link_tag(page_name, '?', 'nonexistent') + page_name
			else:
				return self.link_tag(page_name, page_name, 'nonexistent')

	def page_list(self):
		return filter(self.word_anchored_re.match, os.listdir(self.text_dir))

	def print_search_stats(self, hits, searched):
		print "<p>%d hits " % hits
		print " out of %d pages searched." % searched
