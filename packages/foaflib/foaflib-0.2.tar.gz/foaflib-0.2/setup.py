#!/usr/bin/env python

from setuptools import setup

setup(name="foaflib",
      version="0.2",
      description="Python library for working with FOAF data",
      author="Luke Maurits",
      author_email="luke@maurits.id.au",
      url="http://code.google.com/p/foaflib/",
      packages=["foaflib", "foaflib.classes", "foaflib.helpers", "foaflib.utils"],
      install_requires=["rdflib"]
     )
