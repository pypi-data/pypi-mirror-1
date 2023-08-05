# Article.py is part of The Ming Blog Server
# billy-bob@billy-bob-ming.com

# Copyright (C) 2005, 2006  Richard Harris, TinPenguin
# Released under the GNU General Public License
# (See the included COPYING file)

# The Ming Blog Server is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# The Ming Blog Server is distributed in the hope that they will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with The Ming Blog Server; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import os

class Article:
	BEGIN = "\n<div class=\"entry\">\n"
	END = "\n</div>\n"

	def __init__(self, lib, dir, author, email):
		"""Setup for byline"""
		self.lib = lib
		self.dir = dir
		self.author = author
		self.email = email


	def get_article(self, article, log=0):
		lines = self.lib.read_lines(os.path.join(self.dir,"entries",article))
		hdr = lines[0].split(":")
		title = hdr[0]
		cat = hdr[1]
		date = self.lib.get_date(article)
		byline = "\n<h4>Posted by <a href=\"mailto:"+self.email+"\">"+self.author+\
				 "</a> in "+cat+" on "+date+"</h4>\n"
		byline = "\n<div class=\"byline\">"+byline+"</div>"
		# article
		a = ''.join(lines[1:])
		a = self.BEGIN + "\n<h3>"+ title + "</h3>\n"+ a + byline + self.END
		#logging (if Ming Server installation)
		blog = os.path.basename(self.dir)
		if (log):
			self.lib.log_article(article, title, blog)
		return a
