#!/usr/bin/env python

__revision__ = "$Id: setup.py 21283 2003-04-04 19:53:43Z akuchlin $"

from distutils.core import setup

setup(name = "Sancho",
      version = "0.11",
      description = "Unit testing framework",

      author = "Greg Ward",
      author_email = "gward@mems-exchange.org",
      maintainer = "A.M. Kuchling",
      maintainer_email = "akuchlin@mems-exchange.org",
      url = "http://www.mems-exchange.org/software/sancho/",

      package_dir = {"sancho": "."},
      packages = ["sancho"],
      scripts = ["scripts/run_sancho_tests"],
     )
