#!/usr/bin/env python

from distutils.core import setup

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
import simples3
intro = open("README", "U").read()
usage = "\nUsage\n-----\n\n" + simples3.__doc__
changes = open("changes.rst", "U").read()
long_description = intro + usage + "\n" + changes

setup(name="simples3", version=simples3.__version__,
      url="http://lericson.blogg.se/code/",
      author="Ludvig Ericson", author_email="ludvig@lericson.se",
      description="Simple, quick Amazon AWS S3 interface",
      long_description=long_description,
      packages=["simples3"])
