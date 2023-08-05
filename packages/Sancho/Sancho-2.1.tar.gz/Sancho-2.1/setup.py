#!/usr/bin/env python
"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/sancho/setup.py $
$Id: setup.py 27128 2005-08-01 21:00:30Z dbinger $
"""
from distutils.core import setup

setup(name = "Sancho",
      version = "2.1",
      description = "A simple unit testing framework",
      author = "CNRI",
      author_email = "webmaster@mems-exchange.org",
      url = "http://www.mems-exchange.org/software/sancho/",
      license = "see LICENSE.txt",
      package_dir = {"sancho": "."},
      packages = ["sancho"],
      scripts = ["urun.py"],
      platforms = ['Python 2.3'],
     )
