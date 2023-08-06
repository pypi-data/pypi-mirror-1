#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
"""
upload doc :

./setup.py register
python2.5 setup.py bdist_egg upload
python2.6 setup.py bdist_egg upload

"""
setup(
      name="yserv",
      version="1.0",
      #~ packages=['.']
      scripts = ['yserv'],

        author = "manatlan",
        author_email = "me@manatlan.com",
        description = "A simple commandline to serve on-demand files thru a builtin http server. Just give files you want to serve to yserv, and it will act as an http server, letting people download your files during a session.",
        license = "GPL v2",
        url = "http://www.manatlan.com/page/yserv",
        keywords=['command', 'webserver', 'share', 'p2p'],
      )
