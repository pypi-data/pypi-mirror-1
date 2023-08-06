#!/usr/bin/env python
from distutils.core import setup, Extension
from sys import version

trove = filter(bool, """
License :: OSI Approved :: BSD License
Operating System :: POSIX
Programming Language :: Python
Topic :: Software Development :: Libraries :: Python Modules
Topic :: System :: Systems Administration :: Authentication/Directory
""".splitlines())

if version < "2.2.3":
    from distutils.dist import DistributionMetadata
    DistributionMetadata.classifiers = None
    DistributionMetadata.download_url = None

setup(name="flamboyantsshd", version="0.1r1", author="Ludvig Ericson",
    author_email="ludvig.ericson@gmail.com",
    description="iptables-based autoblocker for the OpenSSH daemon",
    packages={"flamboyantsshd": "flamboyantsshd"}, classifiers=trove)
