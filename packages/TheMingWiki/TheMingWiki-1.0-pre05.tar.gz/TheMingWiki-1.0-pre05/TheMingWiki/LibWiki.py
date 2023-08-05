
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

	def editlog_lines(self):
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

	def is_public(self, PageName):
		public = self.open(self.public_txt).readlines()
		if PageName+"\n" in public:
			return 1
		return 0

	def last_modified(self, PageName):
		fname = self._text_filename(PageName)
		if path.exists(fname):
			modtime = localtime(os.stat(fname)[stat.ST_MTIME])
			return strftime(self.datetime_fmt, modtime)
		else:
			return None

	def link_to(self, PageName):
		if path.exists(path.join(self.text_dir, PageName)):
			return self._link_tag(PageName)
		else:
			if self.nonexist_qm:
				return self._link_tag(PageName, '?', 'nonexistent') + PageName
			else:
				return self._link_tag(PageName, PageName, 'nonexistent')

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
		print "</table>"

	def print_search_stats(self, hits, searched):
		print "<p>%d hits " % hits
		print " out of %d pages searched." % searched

	def read_body(self, PageName):
		try:
			return self.open(self._text_filename(PageName), 'rt').read()
		except IOError, er:
			if er.errno == errno.ENOENT:
				# just doesn't exist, use default
				return 'Describe %s here.' % PageName
			else:
				raise er

	def gen_header(self, text, link=None, msg=None):
		header = "<head><title>%s</title>" % text
		if self.css_url:
			header += '<link rel="stylesheet" type="text/css" href="%s">' % self.css_url
		header += '''</head>
		<body>
		<center>
		<table width="95%"><tr><td>
		<h1>'''
		if self.logo_string:
			header += self.logo_string
		if link:
			header += '<a href="%s">%s</a>' % (link, text)
		else:
			header += text
		header += '</h1>'
		if msg: header += msg
		header += '<hr>'
		return header

	def write_file(self, PageName, text):
		tmp_filename = self._tmp_filename(PageName)
		self.lockopen(tmp_filename, 'wt').write(text)
		text = self._text_filename(PageName)
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


	def save_page(self, PageName, newtext):
		self.write_file(PageName, newtext)
		remote_name = environ.get('REMOTE_ADDR', '')
		self._editlog_add(PageName, remote_name)
		
	#
	# Private Methods
	#		


	def _editlog_add(self, PageName, host):
		editlog = self.lockopen(self.editlog, 'a+')
		try: 
			editlog.seek(0, 2)	# to end
			editlog.write(string.join((PageName, host, `time.time()`), "\t") + "\n")
		finally:
			editlog.close()

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

	def _text_filename(self, PageName):
		return path.join(self.text_dir, PageName)

	def _tmp_filename(self, PageName):
		return path.join(self.text_dir, ('#' + PageName + '.' + `os.getpid()` + '#'))
