#!/usr/bin/env python
from setuptools import setup
setup(name="scribe",
      version="0.3.1",
      py_modules=['scribe'],
      author="Andy Smith",
      author_email="scribe_py@anarkystic.com",
      description="Log like it's going out of style",
      license="MIT License",
      long_description="A library that hacks some logging bits into your code so that a quick -v at the command-line will put you into debug output",
      classifiers=["Development Status :: 4 - Beta",
                   "Intended Audience :: Developers",
                   "License :: OSI Approved :: MIT License",
                   "Natural Language :: English",
                   "Operating System :: OS Independent",
                   "Programming Language :: Python",
                   "Topic :: Software Development"],
      url="http://anarkystic.com/w/ScribePy")
