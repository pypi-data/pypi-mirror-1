#!/usr/bin/python
# Copyright (C) 2008, Charles Wang.
# Author: Charles Wang <charlesw1234@163.com>

__version__ = '0.1.1'

import os.path

from setuptools import setup, find_packages, Extension

setup(name = "pickey",
      version = __version__,
      description = "A WSGI Application which can generate authentication key picture.",
      long_description = """\
You may want to provide a picture which contain a human readable keycode
when register or login. This picture is difficult to be recognized by computer
but easily for human. So some site require it to ban robot.

pickey is a WSGI middleware which can generate this keycode for the
application wrapped. Many options are provided to adjust the outlooking of
the generated picture.

pickey use "gd" to render picture and use "Beaker" to support session.
""",
      classifiers = [
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware",
        ],
      keywords = 'web application middleware wsgi',
      author = 'Charles Wang',
      author_email = 'charlesw1234@163.com',
      url = '',
      license = 'MIT',
      packages = find_packages(),
      install_requires = ["Paste>=1.7", "Beaker>=0.9.4"],
      ext_modules = [Extension('_pickey',
                               [os.path.join('srcs', '_pickey.c')],
                               libraries = ['gd'])],
      entry_points = """
      [paste.filter_factory]
          pickey = pickey:pickey_filter_factory
      [paste.filter_app_factory]
          pickey = pickey:application
      """)
