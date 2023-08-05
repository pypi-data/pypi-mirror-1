
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

import errno, string, time, os, stat
from os import path, environ
from time import localtime, strftime
if os.name == "nt":
	import msvcrt, sys
	Lib3._lock_sh = Lib3._lock_ex = Lib3._lock_win
	msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)
else:
	import fcntl

class LibWiki:

	BOM_UTF8 = "\xef\xbb\xbf"
	BOM_UTF16_LE = "\xff\xfe"
	BOM_UTF16_BE = "\xfe\xff"
	datetime_fmt = '%a %d %b %Y %I:%M %p'
	nonexist_qm = 0	# show '?' for nonexistent?

	def __init__(self, data, logo, css_url, form, word_anchored_re):
		self.text_dir = path.join(data, 'text')
		self.editlog = path.join(data, 'editlog')
		self.access_txt = path.join(data, 'access.txt')
		self.public_txt = path.join(data, 'public.txt')
		self.logo_string = logo
		self.css_url = css_url
		self.form = form
		self.word_anchored_re = word_anchored_re
		return

	#
	# Public Methods
	#

	def editlog_add(self, page_name, host):
		editlog = self.lockopen(self.editlog, 'a+')
		try: 
			editlog.seek(0, 2)	# to end
			editlog.write(string.join((page_name, host, `time.time()`), "\t") + "\n")
		finally:
			editlog.close()

	def editlog_raw_lines(self):
		editlog = self.open(self.editlog, 'rt')
		try:
			return editlog.readlines()
		finally:
			editlog.close()

	def get_scriptname(self):
		return environ.get('SCRIPT_NAME', '')

	def has_access(self, usr, pwd):
		access = self.open(self.access_txt).readlines()
		if usr+":"+pwd+"\n" in access:
			return 1
		return 0

	def is_public(self, pagename):
		public = self.open(self.public_txt).readlines()
		if pagename+"\n" in public:
			return 1
		return 0

	def last_modified(self, page_name):
		fname = self._text_filename(page_name)
		if path.exists(fname):
			modtime = localtime(os.stat(fname)[stat.ST_MTIME])
			return strftime(self.datetime_fmt, modtime)
		else:
			return None

	def link_to(self, page_name):
		if path.exists(path.join(self.text_dir, page_name)):
			return self._link_tag(page_name)
		else:
			if self.nonexist_qm:
				return self._link_tag(page_name, '?', 'nonexistent') + page_name
			else:
				return self._link_tag(page_name, page_name, 'nonexistent')

	def page_list(self):
		return filter(self.word_anchored_re.match, os.listdir(self.text_dir))

	def print_footer(self, name, editable=1, mod_string=None):
		base = self.get_scriptname()
		print '<hr>'
		if editable:
			print self._link_tag('?edit='+name, 'EditText')
			print "of this page"
			if mod_string:
				print "(last modified %s)" % mod_string
			print '<br>'
		print self._link_tag('FindPage?value='+name, 'FindPage')
		print " by browsing, searching, or an index"

	def print_search_stats(self, hits, searched):
		print "<p>%d hits " % hits
		print " out of %d pages searched." % searched

	def read_body(self, page_name):
		try:
			return self.open(self._text_filename(page_name), 'rt').read()
		except IOError, er:
			if er.errno == errno.ENOENT:
				# just doesn't exist, use default
				return 'Describe %s here.' % page_name
			else:
				raise er

	def send_title(self, text, link=None, msg=None):
		print "<head><title>%s</title>" % text
		if self.css_url:
			print '<link rel="stylesheet" type="text/css" href="%s">' % self.css_url
		print "</head>"
		print '<body><h1>'
		if self.logo_string:
			print self.logo_string
		if link:
			print '<a href="%s">%s</a>' % (link, text)
		else:
			print text
		print '</h1>'
		if msg: print msg
		print '<hr>'

	def write_file(self, page_name, text):
		tmp_filename = self._tmp_filename(page_name)
		self.lockopen(tmp_filename, 'wt').write(text)
		text = self._text_filename(page_name)
		if os.name == 'nt':
			try:
				os.remove(text)
			except OSError, er:
				if er.errno <> errno.ENOENT: raise er
		# XXX: POSIX rename ought to replace.
		os.rename(tmp_filename, text)

	def open(self, fname, *args):
		"""open() wrapper: if the file is opened for reading, we look
		for a possible BOM and (if we do find one) print some headache-saving
		info about it, moving to the beginning of the file's actual content
		"""
		f = open(fname, *args)
		if hasattr(f, "read"):
			bytes = f.read(2)
			if bytes in (self.BOM_UTF16_LE, self.BOM_UTF16_BE):
				raise IOError, (42, os.strerror(42), bytes)
			elif (bytes + f.read(1)) == self.BOM_UTF8:
				pass
			else:
				f.seek(0)
		return f

	def lockopen(self, fname, mode="r", create=True, block=False, retries=3, shared=-1):
		"""
		opens a file and applies a lock to it. By default, the lock
		will be a shared one if the file is opened for reading ONLY; exclusive
		in all other cases. This behaviour can be overridden by setting the 'shared'
		parameter to the correct boolean value. NOTES:
		- 'mode' must be a string following the same rules valid for the built-in
		  'file' function... but: append mode is not recognized, and the 'b' flag
		  has no effect (files are automatically opened in binary mode);
		- locking is *advisory* on Unix, mandatory on Windows;
		- on Windows, the lock will always be strictly exclusive.
		  "Strictly" means that the current process will not be able to map
		  another file descriptor to the locked file (and use it) until this
		  gets unlocked.
		"""
		if mode[0] not in ("a", "r", "w"):
			raise ValueError, "invalid mode " + mode
		EX = True
		if mode.find("+") != -1:
			FLAGS = os.O_RDWR
		elif (mode[0] == "w") or (mode[0] == "a"):
			FLAGS = os.O_WRONLY
		else:
			FLAGS = os.O_RDONLY
			EX = False
		if create:	FLAGS |= os.O_CREAT
		FLAGS |= getattr(os, "O_BINARY", 0)
		fd = os.open(fname, FLAGS)
		if EX == shared: EX ^= 1
		lock = EX and self._lock_ex or self._lock_sh
		for i in range(retries):
			try:
				lock(fd, block)
				fobj = os.fdopen(fd, mode)
				if mode[0] == "w": fobj.truncate()
				return fobj
			except Exception:
				time.sleep(.01)
		else:
			raise IOError, "cannot lock and open " + fname

	#
	# Private Methods
	#		

	def _link_tag(self, params, text=None, ss_class=None):
		if text is None:
			text = params					# default
		if ss_class:
			classattr = 'class="%s" ' % ss_class
		else:
			classattr = ''
		return '<a %s href="%s/%s">%s</a>' % \
			   (classattr, self.get_scriptname(), params, text)

	def _lock_nix(self, mode, fd, block):
		if not block:
			mode |= fcntl.LOCK_NB
		fcntl.lockf(fd, mode)

	def _lock_win(self, fd, block):
		MODE = block and msvcrt.LK_LOCK or msvcrt.LK_NBLCK
		msvcrt.locking(fd, MODE, 1)

	def _lock_sh(self, *args):
		"apply a shared lock"
		self._lock_nix(fcntl.LOCK_SH, *args)

	def _lock_ex(self, *args):
		"apply an exclusive lock"
		self._lock_nix(fcntl.LOCK_EX, *args)

	def _text_filename(self, page_name):
		return path.join(self.text_dir, page_name)

	def _tmp_filename(self, page_name):
		return path.join(self.text_dir, ('#' + page_name + '.' + `os.getpid()` + '#'))
