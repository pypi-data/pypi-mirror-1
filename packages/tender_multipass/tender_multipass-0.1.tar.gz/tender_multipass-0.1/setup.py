#!/usr/bin/env python

from distutils.core import setup

setup(name="tender_multipass",
      version="0.1",
      description="Utilities to work with Tender's multipass authentication",
      author="Michael Richardson",
      author_email="michael@mtrichardson.com",
      url="http://bitbucket.org/mtrichardson/tender-multipass/",
      py_modules=["tender_multipass"],
      install_requires=["M2Crypto"],
      license="MIT License",
)
