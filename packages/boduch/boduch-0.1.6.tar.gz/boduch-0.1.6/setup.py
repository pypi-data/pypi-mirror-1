#!/usr/bin/python

from setuptools import setup, find_packages
setup(name="boduch",\
      version='0.1.6',\
      install_requires = ['zope.interface'],\
      zip_safe=False,\
      packages = find_packages('src'),\
      package_dir = {'':'src'},\
      author = "Adam Boduch",\
      author_email = "adam.boduch@gmail.com",\
      license = "AGPL",\
      url = "http://www.boduch.ca/")

