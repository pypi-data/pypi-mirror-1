#!/usr/bin/env python

# setup.py is part of The Ming Blog Server
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

"""A Honking-good Little Python Blog Server

The TheMingBlogger generates blogs and their indices on the fly.  All
you need is Python in the cgi-bin and permalink data files for the blog
which are uploaded to the entries directory of each blog. Example blogs
are included.  The TheMingBlogger can be used stand-alone with its own
script or you can drop the blog server directory into a Ming Server
installation and it will pull in the blogs automatically."""

import sys, os
from distutils.cmd import Command
from distutils.core import setup
from distutils.command.install_data import install_data

NAME = "The Ming Blog Server"
UNIX_NAME = "TheMingBlogger"
LICENSE = "GNU General Public License"
PLATFORMS = ["any"]
CLASSIFIERS = """
Development Status :: 4 - Beta
Environment :: Web Environment
Intended Audience :: Developers
Intended Audience :: End Users/Desktop
Intended Audience :: System Administrators
License :: OSI Approved :: GNU General Public License (GPL)
Natural Language :: English
Operating System :: OS Independent
Programming Language :: Python
Topic :: Internet :: WWW/HTTP :: Dynamic Content
Topic :: Internet :: WWW/HTTP :: Site Management
"""

get = globals().get

def walk_data(dir):
    result = []
    start = len(dir) + 1
    append = lambda foo, dir, names: result.append((dir[start:] or '.', filter(os.path.isfile, [os.path.join(dir, name) for name in names])))
    os.path.walk(dir, append, None)
    return result

HTDOCS = walk_data('htdocs')
PACKAGES = ['TheMingBlogger']
SCRIPTS = ['cgi-bin/blogger.cgi']

class install(Command):

    prompts = (
        ('lib', ("the path to the cgi-bin directory where The Ming Blog Server will \nbe installed", 0, 1)),
        ('scripts', ("the path to the cgibin directory for The Ming Blog Server script, \nunless you are using the blogs with The Ming Server's ming.cgi", 1, 1)),
        ('htdocs', ("the path to the directory where the example blogs will be \ninstalled", 1, 1))
        )

    def finalize_options(self):
        self.print_header()
        if not self.has_any_option_set():
            self.ask_user()


#=========================== the rest is constant for every package of Billy Bob's

        self.set_undefined_options('build',
                                   ('build_lib', 'build_lib'))

    description = "install " + NAME

    user_options = [
        ('install-lib=', None, "installation directory for Python modules"),
        ('install-scripts=', None, "installation directory for Python scripts"),
        ('install-data=', None, "installation directory for data files"),
        ('install-htdocs=', None, "web server's htdocs directory (for static resources)"),
        ('compile', 'c', "compile .py to .pyc [default]"),
        ('no-compile', None, "don't compile .py files"),
        ('optimize=', 'O',
         "also compile with optimization: -O1 for \"python -O\", "
         "-O2 for \"python -OO\", and -O0 to disable [default: -O0]"),
        ('force', 'f',
         "force installation (overwrite any existing files)")
        ]

    def initialize_options(self):
        self.install_lib = None
        self.install_scripts = None
        self.install_data = None
        self.install_htdocs = None
        self.force = 0
        self.skip_build = 0
        self.build_lib = None
        self.compile = None
        self.optimize = None
        self.root = None

    def ask_user(self):
        i = 0
        for key, options in self.prompts:
            i += 1
            print "(%d)" % i,
            install_dir = self.get_dir(*options)
            setattr(self, "install_" + key, install_dir)

    def get_dir(self, prompt, optional=0, create=1):
        print "Enter %s%s:" % (prompt, optional and " (optional)" or "")
        while 1:
            try:
                install_dir = raw_input("> ").strip()
            except:
                print "\n\nInstallation interrupted by user."
                sys.exit()
            if optional and install_dir == "":
                return None
            elif os.path.exists(install_dir):
                break
            elif create:
                try:
                    os.mkdir(install_dir)
                    break
                except: pass
            print "Please specify a valid%s directory path%s..." % \
                (not create and " (and existing)" or "",
                 optional and ", or press Enter to skip the \ninstallation of this item" or "")
        print
        return install_dir

    def print_header(self):
        print "_" * 76
        print "\n  %s Installation Script" % NAME
        print "_" * 76
        print

    def run(self):
        commands = self.get_sub_commands()
        if commands:
            for cmd_name in commands:
                print "* installing %s..." % cmd_name[8:]
                self.run_command(cmd_name)
            print "\nInstallation completed."
        else:
            print "Nothing to do!"

    def has_lib(self):
        return self.install_lib and self.distribution.packages

    def has_scripts(self):
        return self.install_scripts and self.distribution.scripts

    def has_data(self):
        return self.install_data and self.distribution.data_files

    def has_htdocs(self):
        return self.install_htdocs and get('HTDOCS')

    def has_any_option_set(self):
        if (self.install_lib or
            self.install_data or
            self.install_scripts or
            self.install_htdocs):
               return True
        return False

    sub_commands = [
        ('install_lib',     has_lib),
        ('install_scripts', has_scripts),
        ('install_data',    has_data),
        ('install_htdocs',  has_htdocs)
        ]

class install_htdocs(install_data):

    description = "install static web resources and example files"

    def initialize_options(self):
        install_data.initialize_options(self)
        self.data_files = get('HTDOCS')

    def finalize_options (self):
        self.set_undefined_options('install',
                                   ('install_htdocs', 'install_dir'),
                                   ('root', 'root'),
                                   ('force', 'force'),
                                  )

#-------------------------------------------------------

if sys.version < '2.2.3':
    from distutils.dist import DistributionMetadata
    DistributionMetadata.classifiers = None
    DistributionMetadata.download_url = None

doclines = __doc__.splitlines()

setup(
    verbose = 0,
    cmdclass = {'install': install,
                'install_htdocs': install_htdocs},
    name = UNIX_NAME,
    version = "1.0-pre01",
    license = LICENSE,
    platforms = PLATFORMS,
    classifiers = filter(None, CLASSIFIERS.splitlines()),
    author = "Billy Bob Ming",
    author_email = "billy-bob@billy-bob-ming.com",
    description = doclines[0],
    url = "http://python.org/pypi/%s" % UNIX_NAME,
    long_description = "\n".join(doclines[2:]),
    package_dir = get('PACKAGE_DIR'),
    packages = get('PACKAGES'),
    scripts = get('SCRIPTS'),
    data_files = get('DATA_FILES')
    )
