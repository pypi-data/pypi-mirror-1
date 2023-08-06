#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=4 ts=4 sts=4 et tw=79 :
# Copyright 2008 Ali Polatel <polatel@itu.edu.tr>
# Distributed under the terms of the GNU General Public License v3

from setuptools import setup, find_packages

# Get metadata
from randomorg import __author__ as author
from randomorg import __name__ as name
from randomorg import __license__ as license
from randomorg import __url__ as url
from randomorg import __version__ as version

setup( name = name,
        version = version,
        license = license,
        description = "python module to access random.org for random numbers",
        long_description = open("README").read(),
        author = author.split(' <')[0],
        author_email = author.split(' <')[1].rsplit('>')[0],
        url = url,

        packages = find_packages(exclude=['ez_setup']),

        classifiers = [ "Development Status :: 3 - Alpha",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: GNU General Public License (GPL)",
            "Operating System :: OS Independent",
            "Programming Language :: Python",
            "Topic :: Internet",
            "Topic :: Software Development :: Libraries :: Python Modules", ],
        
        )
