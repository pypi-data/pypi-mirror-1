# -*- coding: utf-8 -*-

try:
  from setuptools import setup
except:
  from distutils.core import setup
import hinagiku

name = hinagiku.__name__.title()
summary = "Web page update checker"
author, email = hinagiku.__author__.split("<")
author = author[:-1]
email = email[:-1]

setup(
  name = name,
  version = hinagiku.__version__,
  author = author,
  author_email = email,
  url = hinagiku.__url__,
  description = summary,
  license = hinagiku.__license__,
  long_description = hinagiku.__doc__,
  platforms = ["any"],
  install_requires = ["dateutil", "PyYAML", "Genshi"],
  packages = ["hinagiku"],
  scripts = ["scripts/hinagiku"],
  zip_safe = False,
)
