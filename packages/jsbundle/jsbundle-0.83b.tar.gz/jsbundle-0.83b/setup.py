#-*- coding:utf-8 -*-
#
# Copyright (C) 2009 - Brantley Harris <brantley.harris@gmail.com>
#
# Distributed under the BSD license

import os
from setuptools import setup, find_packages

setup(name='jsbundle',
      version = '0.83b',
      description = 'A javascript bundling tool.',
      long_description = open('README.txt').read(),
      classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.5",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 3",
        "Programming Language :: JavaScript",
        "Topic :: Internet",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
      ],
      keywords = 'javascript minify bundle js build compile',
      author = 'Brantley Harris',
      author_email = 'brantley.harris@gmail.com',
      url = 'http://www.bitbucket.org/DeadWisdom/jsbundle/',
      download_url = "http://bitbucket.org/DeadWisdom/jsbundle/get/tip.tar.gz",
      license = 'MIT',
      packages = find_packages(exclude=['test', 'doc']),
      zip_safe = True,
      extras_require = {
        'simplejson': ["simplejson"],
      })
