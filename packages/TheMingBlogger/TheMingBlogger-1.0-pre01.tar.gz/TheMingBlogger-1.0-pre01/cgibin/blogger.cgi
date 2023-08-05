#!/usr/bin/python

# blogger.cgi is part of The Ming Blog Server
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

import cgi, os

if os.path.exists("/home/richard/.my_machine"):
	BLOGS_DIRECTORY = "../data/blogs"
else: # for chrooted virtual host accounts
	BLOGS_DIRECTORY = os.path.expanduser("~/data/blogs")

form = cgi.FieldStorage()
if "type" in form.keys():
	if form["type"].value == "ByTitle":
		from TheMingBlogger import ByTitle
		obj = ByTitle.ByTitle()
	elif form["type"].value == "ByCategory":
		from TheMingBlogger import ByCategory
		obj = ByCategory.ByCategory()
	if form["type"].value == "ByDate":
		from TheMingBlogger import ByDate
		obj = ByDate.ByDate()
	obj.print_page()

else:
	from TheMingBlogger import LibBlog
	lb = LibBlog.LibBlog()
	lb.give_headers()
	dir = lb.get_dir()
	author, email, title, tagline = lb.get_text(dir)
	intro = lb.get_lines(dir,"intro")
	footer = lb.get_lines(dir,"footer")
	links = lb.get_lines(dir,"links")
	content = lb.content(dir, author, email)
	page = lb.do_page(dir, title, tagline, intro, footer, links, content)
	print page
	raise SystemExit

