#!/usr/bin/env python

# Copyright (c) 2009 Adroll.com, Valentino Volonghi
# See LICENSE for details.

"""
Distutils installer for turtle.
"""

try:
    # Load setuptools, to build a specific source package
    import setuptools
except ImportError:
    pass

import sys, os
import turtle

install_requires = ["PyYAML>=3.08"]

setup = setuptools.setup
find_packages = setuptools.find_packages

description = """\
Turtle is an HTTP proxy whose purpose is to throttle connections to
specific URLS to avoid breaking terms of usage of those API providers
(like del.icio.us, technorati and so on).
"""

setup(
    name = "turtle",
    author = "Valentino Volonghi",
    author_email = "valentino@adroll.com",
    url = "http://adroll.com/labs",
    description = description,
    license = "MIT License",
    version=turtle.__version__,
    install_requires=install_requires,
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Topic :: Internet',
    ],
    packages=find_packages(exclude=['ez_setup', 'doc', 'examples'])
)
