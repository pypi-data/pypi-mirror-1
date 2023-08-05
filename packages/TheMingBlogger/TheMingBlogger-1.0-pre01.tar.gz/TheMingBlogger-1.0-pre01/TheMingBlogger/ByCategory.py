# ByCategory.py is part of The Ming Blog Server
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
from TheMingBlogger import LibBlog

class ByCategory:

	BEGIN = "<div id=\"permcontent\">\n<h2>Archives</h2>\n<h3>By Category</h3>\n<ul>\n"
	END = "\n</ul>\n</div>\n"

	def __init__(self):
		self.lib = LibBlog.LibBlog()
		self.CGI = self.lib.CGI
		self.DIR = self.lib.DIR
		return

	def __get_titles(self, dir):
		subdir = os.path.join(self.DIR,dir,"entries")
		entries = os.listdir(subdir)
		titles = []
		for x in entries:
			lines = self.lib.read_lines(subdir+os.sep+x)
			tmp = lines[0].split(":")
			titles.append(tmp[1]+":"+tmp[0]+":"+x)
		titles.sort()
		return titles

	def __get_links(self, dir, titles):
		last = ""
		links = []
		for x in titles:
			line = x.split(":")
			if last != line[0]:
				if last != "":
					links.append("</ul>\n")
				links.append("<h3>"+line[0]+"</h3>\n<ul>\n")
				last = line[0]
			links.append("<li><a href=\"/"+self.CGI+"/ming.cgi?blog="+dir+\
						 "&amp;article="+line[2]+"\">"+line[1]+"</a>")
		links = "\n".join(links)
		return self.BEGIN + links + self.END

	def print_page(self):
		self.lib.give_headers()
		dir = self.lib.get_dir()
		titles = self.__get_titles(dir)
		content = self.__get_links(dir, titles)
		intro = self.lib.get_lines(dir,"intro")
		links = self.lib.get_lines(dir, "links")
		author, email, title, tagline = self.lib.get_text(dir)
		footer = self.lib.get_lines(dir,"footer")
		page = self.lib.do_page(dir, title, tagline, intro, footer, links, content)
		print page
