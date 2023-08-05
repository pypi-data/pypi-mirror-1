#!/usr/bin/env python
from distutils.core import setup
from sys import version

trove = filter(bool, """
Development Status :: 4 - Beta
Intended Audience :: Developers
Operating System :: OS Independent
Programming Language :: Python
Topic :: Communications :: Chat :: Internet Relay Chat
Topic :: Software Development :: Libraries :: Python Modules
""".splitlines())

if version < "2.2.3":
    from distutils.dist import DistributionMetadata
    DistributionMetadata.classifiers = None
    DistributionMetadata.download_url = None

setup(name="pysimpirc", version="0.1.2", description="Simple IRC module",
    author="Ludvig Ericson", author_email="ludvig.ericson@gmail.com",
    url="http://labs.lericson.se/experiments/pysimpirc/",
    py_modules=["token_bucket", "pysimpirc"], classifiers=trove)
