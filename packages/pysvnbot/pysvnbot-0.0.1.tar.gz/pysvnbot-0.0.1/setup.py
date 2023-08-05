#!/usr/bin/env python
from distutils.core import setup
from sys import version

trove = filter(bool, """
Development Status :: 3 - Alpha
Environment :: Other Environment
Intended Audience :: Developers
Intended Audience :: System Administrators
Operating System :: POSIX
Programming Language :: Python
Topic :: Communications :: Chat :: Internet Relay Chat
Topic :: Software Development :: Version Control
Topic :: System :: Monitoring
Topic :: Software Development :: Build Tools
""".splitlines())

if version < "2.2.3":
    from distutils.dist import DistributionMetadata
    DistributionMetadata.classifiers = None
    DistributionMetadata.download_url = None

setup(name="pysvnbot", version="0.0.1", description="Subversion commit log tracking bot",
    author="Ludvig Ericson", author_email="ludvig.ericson@gmail.com",
    url="http://lericson.se/", packages=["pysvnbot"], classifiers=trove)
