#!/usr/bin/python
from setuptools import setup, Extension
import sys

_growl = Extension('_growl',
                    extra_link_args = ["-framework","CoreFoundation"],
                    sources = ['libgrowl.c'])
_growlImage = Extension('_growlImage',
                        extra_link_args = ["-framework","Cocoa"],
                        sources = ['growlImage.m'])

if sys.platform.startswith("darwin"):
    modules = [_growl, _growlImage]
else:
    modules = []

setup(name="py-Growl",
      version="0.0.7",
      description="Python bindings for posting notifications to the Growl daemon",
      author="Victor Ng",
      author_email="bdash@users.sourceforge.net",
      url="http://www.assembla.com/spaces/nosegrowl/",
      py_modules=["Growl"],
      ext_modules = modules )

