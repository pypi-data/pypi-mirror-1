# LibBlog.py is part of The Ming Blog Server
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

import os, re
from Article import Article
from stat import S_ISDIR, ST_MODE
from dircache import listdir
from __main__ import BLOGS_DIRECTORY

class LibBlog:

	CGI = "cgibin"
	DIR = BLOGS_DIRECTORY
	N = 8
	MONTHS = {
		"01":"January",
		"02":"February",
		"03":"March",
		"04":"April",
		"05":"May",
		"06":"June",
		"07":"July",
		"08":"August",
		"09":"September",
		"10":"October",
		"11":"November",
		"12":"December",
		}

	def __init__(self, form=None):
		if not form:
			try:
				from TheMingServer import form
			except:
				import cgi
				form = cgi.FieldStorage()
		self.DATA = form

	def __surNLine(self, text):
		"""For surrounding text with newlines"""
		return "\n"+text+"\n"

	def read_lines(self, fname):
		try:
			f = open(fname)
			lines = f.readlines()
			f.close()
		except:
			lines = []
		return lines

	def content(self, dir, author, email):
		"""Gets information from each entry using Article.py"""
		if self.DATA.has_key('article'): # For viewing one specific entry
			article = Article(self, os.path.join(self.DIR, dir), author, email)
			a = article.get_article(self.DATA['article'].value, 1)
			return a
		else: # For viewing all entries (default)
			c = []
			files = listdir(os.path.join(self.DIR, dir, 'entries'))
			files.sort()
			if len(files) > self.N: files = files[-self.N:]
			files.reverse()
			article = Article(self, os.path.join(self.DIR, dir), author, email)
			for file in files:
				a = article.get_article(file)
				c.append(a)
			return ''.join(c)

	def do_page(self, dir, title, tagline, intro, footer, links, content):
		"""Puts everything into the HTML template, blog.html"""
		lines = self.read_lines(os.path.join(self.DIR, dir, 'blog.html'))
		sfooter = self.read_lines(os.path.join(self.DIR, 'site.footer'))
		if not (sfooter == []):
			lines = lines[:lines.index("<!--site footer-->\n")]+sfooter+\
					lines[lines.index("<!--site footer-->\n"):]
		new = []
		head = 1
		for line in lines:
			if line.find("</head") != -1:
				head = 0
			elif head:
				line = re.sub("\$DIR", dir, line)
				line = re.sub("\$TITLE", title, line)
			if line.find("<div") != -1: # Put right information in each <div>
				if line.find('"title"') != -1: line = self.__surNLine(line+title)
				if line.find('"tagline"') != -1: line = self.__surNLine(line+tagline)
				if line.find('"intro"') != -1: line = self.__surNLine(line+intro)
				if line.find('"footer"') != -1: line = self.__surNLine(line+footer)
				if line.find('"links"') != -1: line = self.__surNLine(line+links)
				if line.find('"content"') != -1: line = self.__surNLine(line+content)
			new.append(line)
		return ''.join(new)

	def get_date(self, article):
		"""Formats date based on article filename"""
		str = article[0:8]
		yr = str[:4]
		mo = str[4:6]
		mo = self.MONTHS[mo]
		dy = str[6:8]
		return mo+" "+dy+", "+yr

	def get_dir(self):
		"""Finds out the blog wanted, and sets the directory accordingly"""
		if not self.DATA.has_key('blog'): # Probably reached here by error
			return "none"
		dir = self.DATA['blog'].value
		if not S_ISDIR(os.stat(os.path.join(self.DIR, dir))[ST_MODE]): # Ditto
			return "no_dir"
		else:
			return dir

	def get_lines(self, dir, name):
		"""Reads lines from any given file starting with 'blog.' """
		lines = self.read_lines(os.path.join(self.DIR, dir, 'blog.'+name))
		if (name == "links"):				# pull /blogs/site.links
			lines = lines + self.read_lines(os.path.join(self.DIR, 'site.links'))
		return ''.join(lines)

	def get_text(self, dir):
		"""Gets general blog information from blog.txt configuration file"""
		lines = self.read_lines(os.path.join(self.DIR, dir, 'blog.txt'))
		# Grabs each part of file, using colon seperated values
		author = lines[0].split(":")[1].strip()
		email = lines[1].split(":")[1].strip()
		title = lines[2].split(":")[1].strip()
		tagline = lines[3].split(":")[1].strip()
		return author, email, title, tagline

	def give_headers(self):
		print "Content-Type: text/html\n"

	def log_article(self, article, title, blog):
		try:
			from TheMingServer import Logger
			logger = Logger()
			title = blog.capitalize()+": "+title
			logger.log_entry(title, "blog="+blog+"&article="+article)
		except:
			pass
		return
