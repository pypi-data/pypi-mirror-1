
# PageFormatter -- a part of The Ming Wiki

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

import re, string, time
from cStringIO import StringIO
from socket import gethostbyaddr
from time import localtime, strftime

class PageFormatter:
	"""Object that turns Wiki markup into HTML.

	All formatting commands can be parsed one line at a time, though
	some state is carried over between lines.
	"""
	show_hosts = 0	# show hostnames?
	changed_time_fmt = ' . . . . [%I:%M %p]'
	date_fmt = '%a %d %b %Y'
	
	def __init__(self, lib):
		self.form = lib.form
		self.lib = lib
		self.is_em = self.is_b = 0
		self.list_indents = []
		self.in_pre = 0

	def format_page(self, raw):
		self.raw = raw
		# For each line, we scan through looking for magic
		# strings, outputting verbatim any intervening text
		scan_re = re.compile(
			r"(?:(?P<emph>'{2,3})"
			+ r"|(?P<ent>[<>&])"
			+ r"|(?P<word>\b(?:[A-Z][a-z]+){2,}\b)"
			+ r"|(?P<rule>-{4,})"
			+ r"|(?P<url>(http|ftp|nntp|news|mailto)\:[^\s'\"]+\S)"
			+ r"|(?P<email>[-\w._+]+\@[\w.-]+)"
			+ r"|(?P<li>^\s+\*)"
			+ r"|(?P<pre>(\{\{\{|\}\}\}))"
			+ r"|(?P<macro>\[\[(TitleSearch|FullSearch|WordIndex"
			+ r"|TitleIndex|RecentChanges)\]\])"
			+ r")")
		blank_re = re.compile("^\s*$")
		bullet_re = re.compile("^\s+\*")
		indent_re = re.compile("^\s*")
		eol_re = re.compile(r'\r?\n')
		raw = string.expandtabs(self.raw)

		body = ""
		for line in eol_re.split(raw):
			if not self.in_pre:
				# XXX: Should we check these conditions in this order?
				if blank_re.match(line):
					body += '<p>'
					continue
				indent = indent_re.match(line)
				body += self._indent_to(len(indent.group(0))) +"\n"
			body += re.sub(scan_re, self._replace, line) +"\n"
		if self.in_pre: body += '</pre>'
		body += self._undent()
		return body
	
	#
	# Private Methods
	#

	def _indent_level(self):
		return len(self.list_indents) and self.list_indents[-1]

	def _indent_to(self, new_level):
		s = ''
		while self._indent_level() > new_level:
			del(self.list_indents[-1])
			s = s + '</ul>\n'
		while self._indent_level() < new_level:
			self.list_indents.append(new_level)
			s = s + '<ul>\n'
		return s

	def _macro_repl(self, word):
		macro_name = word[2:-2]
		return apply(getattr(self, '_macro_' + macro_name), ())		

	def _make_index_key(self):
		s = '<p><center>'
		links = map(lambda ch: '<a href="#%s">%s</a>' % (ch, ch), string.lowercase)
		s = s + string.join(links,' | ')
		s = s + '</center><p>'
		return s

	def _replace(self, match):
		for type, hit in match.groupdict().items():
			if hit:
				return apply(getattr(self, '_' + type + '_repl'), (hit,))
		else:
			raise "Can't handle match " + `match`

	def _undent(self):
		res = '</ul>' * len(self.list_indents)
		self.list_indents = []
		return res

	def _url_split(self, word):
		punc = ""
		if word.find("|") != -1:
			url, name = word.split("|")
			if name[-1] in string.punctuation:
				punc = name[-1]
				name = name[:-1]
		else:
			url = name = word
			if name[-1] in string.punctuation:
				punc = name[-1]
				url = name = name[:-1]
		return url, name, punc

	#
	# Repl Methods
	#

	def _email_repl(self, word):
		url, name, punc = self._url_split(word)
		return '<a href="mailto:%s">%s</a>%s' % (url, name, punc)

	def _emph_repl(self, word):
		if len(word) == 3:
			self.is_b = not self.is_b
			return ['</b>', '<b>'][self.is_b]
		else:
			self.is_em = not self.is_em
			return ['</em>', '<em>'][self.is_em]

	def _ent_repl(self, s):
		return {'&': '&amp;',
				'<': '&lt;',
				'>': '&gt;'}[s]

	def _li_repl(self, match):
		return '<li>'

	def _pre_repl(self, word):
		if word == '{{{' and not self.in_pre:
			self.in_pre = 1
			return '<pre>'
		elif self.in_pre:
			self.in_pre = 0
			return '</pre>'
		else:
			return ''

	def _rule_repl(self, word):
		s = self._undent()
		if len(word) <= 4:
			s = s + "\n<hr>\n"
		else:
			s = s + "\n<hr size=%d>\n" % (len(word) - 2 )
		return s

	def _url_repl(self, word):
		url, name, punc = self._url_split(word)
		return '<a href="%s">%s</a>%s' % (url, name, punc)

	def _word_repl(self, word):
		return self.lib.link_to(word)

	#
	# Macros 
	#

	def _macro_TitleSearch(self):
		return self._macro_search("titlesearch")

	def _macro_FullSearch(self):
		return self._macro_search("fullsearch")

	def _macro_search(self, type):
		if self.form.has_key('value'):
			default = self.form["value"].value
		else:
			default = ''
		return """<form method=get>
		<input name=%s size=30 value="%s"> 
		<input type=submit value="Go">
		</form>""" % (type, default)

	def _macro_WordIndex(self):
		s = self._make_index_key()
		pages = list(self.lib.page_list())
		map = {}
		word_re = re.compile('[A-Z][a-z]+')
		for name in pages:
			for word in word_re.findall(name):
				try:
					map[word].append(name)
				except KeyError:
					map[word] = [name]

		all_words = map.keys()
		all_words.sort()
		last_letter = None
		for word in all_words:
			letter = string.lower(word[0])
			if letter <> last_letter:
				s = s + '<a name="%s"><h3>%s</h3></a>' % (letter, letter)
				last_letter = letter

			s = s + '<b>%s</b><ul>' % word
			links = map[word]
			links.sort()
			last_page = None
			for name in links:
				if name == last_page: continue
				s = s + '<li>' + self.lib.link_to(name)
			s = s + '</ul>'
		return s

	def _macro_TitleIndex(self):
		s = self._make_index_key()
		pages = list(self.lib.page_list())
		pages.sort()
		current_letter = None
		for name in pages:
			letter = string.lower(name[0])
			if letter <> current_letter:
				s = s + '<a name="%s"><h3>%s</h3></a>' % (letter, letter)
				current_letter = letter
			else:
				s = s + '<br>'
			s = s + self.lib.link_to(name)
		return s

	def _macro_RecentChanges(self):
		lines = self.lib.editlog_lines()
		lines.reverse()

		ratchet_day = None
		done_words = {}
		buf = StringIO()
		for line in lines:
			PageName, addr, ed_time = line.split('\t')
			# year, month, day, DoW
			time_tuple = localtime(float(ed_time))
			day = tuple(time_tuple[0:3])
			if day <> ratchet_day:
				buf.write('<h3>%s</h3>' % strftime(self.date_fmt, time_tuple))
				ratchet_day = day

			if done_words.has_key(PageName):
				continue

			done_words[PageName] = 1
			buf.write(self.lib.link_to(PageName))
			if self.show_hosts:
				buf.write(' . . . . ')
				try:
					buf.write(gethostbyaddr(addr)[0])
				except:
					buf.write("(unknown)")
			if self.changed_time_fmt:
				buf.write(time.strftime(self.changed_time_fmt, time_tuple))
			buf.write('<br>')

		return buf.getvalue()
