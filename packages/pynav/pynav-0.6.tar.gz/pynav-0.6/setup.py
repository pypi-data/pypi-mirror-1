#!/usr/bin/python
#  -*- coding=utf-8 -*-
from setuptools import setup, find_packages

setup(
        name = "pynav",
        version = "0.6",
        packages=find_packages(),
        # metadata for upload to PyPI
        author = "sloft",
        author_email = "nomail@example.com",
        description = "Python programmatic web browser to fetch data and test web sites",
        license = "GPL3",
        keywords = ["programmatic", "web", "browser"],
        url = "http://bitbucket.org/sloft/pynav/",
        download_url = "http://bitbucket.org/sloft/pynav/downloads/",
	classifiers = [
	"Programming Language :: Python",
	"Operating System :: OS Independent",
	"License :: OSI Approved :: GNU General Public License (GPL)",
	"Development Status :: 4 - Beta",
	"Environment :: Console",
	"Topic :: Internet",
	"Intended Audience :: Developers",
	"Topic :: Internet :: WWW/HTTP",
	"Topic :: Internet :: WWW/HTTP :: Browsers",
	"Topic :: Internet :: WWW/HTTP :: Indexing/Search",
	"Topic :: Internet :: WWW/HTTP :: Site Management",
	"Topic :: Internet :: WWW/HTTP :: Site Management :: Link Checking",
	"Topic :: Software Development :: Libraries",
	"Topic :: Software Development :: Libraries :: Python Modules",
	],
        long_description = """\
Python programmatic web browser to fetch data and test web sites
________________________________________________________________

Features:

-Post authentication
-User agent support
-Automatic cookie handling
-HTTP Basic Authentication support
-HTTPS support
-Proxy support
-Timeout support
-Reg exp searching
-Links fetching with reg exp filter
-History (pages, posts and responses)
-Save and load history from a file and replay navigation
-Random sleep time beetween pages
-Errors handling
-Document type and server headers information, real url (in case of redirection)
_______________________________________________________________

Bug reporting and features asking are welcome.
Ask your questions and talk about this module on Google groups :
http://groups.google.com/group/pynav
Or on the forums :
https://sourceforge.net/projects/pynav/forums"""
)
