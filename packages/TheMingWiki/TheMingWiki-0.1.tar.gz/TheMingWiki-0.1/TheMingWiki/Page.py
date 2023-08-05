
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

import time, os, string, re, errno, stat
from os import path, environ
from time import localtime, strftime

import PageFormatter

#
#  Class Page
#

class Page:

	datetime_fmt = '%a %d %b %Y %I:%M %p'

	def __init__(self, lib, text_dir, page_name):
		self.pf = PageFormatter.PageFormatter(lib)
		self.page_name = page_name
		self.text_dir = text_dir
		self.lib = lib

	def split_title(self):
		# look for the end of words and the start of a new word,
		# and insert a space there
		return re.sub('([a-z])([A-Z])', r'\1 \2', self.page_name)

	def _text_filename(self):
		return path.join(self.text_dir, self.page_name)

	def _tmp_filename(self):
		return path.join(self.text_dir, ('#' + self.page_name + '.' + `os.getpid()` + '#'))

	def exists(self):
		try:
			os.stat(self._text_filename())
			return 1
		except OSError, er:
			if er.errno == errno.ENOENT:
				return 0
			else:
				raise er

	def get_raw_body(self):
		try:
			return open(self._text_filename(), 'rt').read()
		except IOError, er:
			if er.errno == errno.ENOENT:
				# just doesn't exist, use default
				return 'Describe %s here.' % self.page_name
			else:
				raise er

	def send_page(self, msg=None):
		link = self.lib.get_scriptname() + '?fullsearch=' + self.page_name
		self.lib.send_title(self.split_title(), link, msg)
		self.pf.print_html(self.get_raw_body())
		self.lib.print_footer(self.page_name, 1, self._last_modified())


	def _last_modified(self):
		if not self.exists():
			return None
		modtime = localtime(os.stat(self._text_filename())[stat.ST_MTIME])
		return strftime(self.datetime_fmt, modtime)

	def send_editor(self):
		self.lib.send_title('Edit ' + self.split_title())
		print '<form method="post" action="%s">' % (self.lib.get_scriptname())
		print '<input type=hidden name="savepage" value="%s">' % (self.page_name)
		raw_body = string.replace(self.get_raw_body(), '\r\n', '\n')
		print """<textarea wrap="virtual" name="savetext" rows="17"
				 cols="80">%s</textarea>""" % raw_body
		print """<br><input type=submit value="Save">
				 <input type=reset value="Reset">
				 """
		print "<br>"
		print "</form>"
		print "<p>" + self.lib.link_to('EditingTips')
				 

	def _write_file(self, text):
		tmp_filename = self._tmp_filename()
		open(tmp_filename, 'wt').write(text)
		text = self._text_filename()
		if os.name == 'nt':
			# XXX: POSIX rename ought to replace.
			try:
				os.remove(text)
			except OSError, er:
				if er.errno <> errno.ENOENT: raise er
		os.rename(tmp_filename, text)


	def save_text(self, newtext):
		self._write_file(newtext)
		remote_name = environ.get('REMOTE_ADDR', '')
		self.lib.editlog_add(self.page_name, remote_name)
