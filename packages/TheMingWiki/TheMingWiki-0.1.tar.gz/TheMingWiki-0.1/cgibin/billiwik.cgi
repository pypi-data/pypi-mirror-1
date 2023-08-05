#!/usr/bin/python

# The Ming Wiki -- a fork of Martin Pool's piki

__version__ = '0.1'

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

from os import path

#  USER CONSTS
if path.exists(path.expanduser("~/.my_machine")):
	data_dir = '../files/wiki/'
else:
	data_dir = '~/files/wiki/'
css_url = '/CSS/ming/billiwik.css' # path to stylesheet or ''
logo = '<img src="/img/ming/billiwik.jpg" border=0 alt="billiwik">'
# END USER CONSTS

from TheMingWiki import Wiki
wiki = Wiki.Wiki(data_dir, css_url, logo)
wiki.start()

