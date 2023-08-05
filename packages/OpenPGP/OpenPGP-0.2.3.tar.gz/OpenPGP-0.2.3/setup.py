#!/usr/bin/env python

PACKAGE_NAME = "OpenPGP"
PACKAGE_VERSION = "0.2.3"

import os

from distutils.core import setup

join = os.sep.join

setup(name=PACKAGE_NAME,
      version=PACKAGE_VERSION,
      description="RFC 2440 (OpenPGP) implementation",
      author="PK",
      author_email="poiboy@safe-mail.net",
      url="http://www.aonalu.net/openpgp",
      packages=[join(['src','openpgp']),
                join(['src','openpgp','sap']),
                join(['src','openpgp','sap','pkt']),
                join(['src','openpgp','sap','msg']),
                join(['src','openpgp','sap','util'])])

