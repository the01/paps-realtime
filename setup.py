#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
# from __future__ import unicode_literals

__author__ = "d01 <Florian Jung>"
__email__ = "jungflor@gmail.com"
__copyright__ = "Copyright (C) 2015-16, Florian JUNG"
__license__ = "MIT"
__version__ = "0.1.2"
__date__ = "2016-03-31"
# Created: 2015-09-20 05:30

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
import sys
import os
import re


if sys.argv[-1] == "build":
    os.system("python setup.py clean sdist bdist bdist_egg bdist_wheel")


def get_version():
    """
    Parse the version information from the init file
    """
    version_file = os.path.join("paps_realtime", "__init__.py")
    initfile_lines = open(version_file, "rt").readlines()
    version_reg = r"^__version__ = ['\"]([^'\"]*)['\"]"
    for line in initfile_lines:
        mo = re.search(version_reg, line, re.M)
        if mo:
            return mo.group(1)
    raise RuntimeError(
        u"Unable to find version string in {}".format(version_file)
    )


version = get_version()
requirements = open("requirements.txt", "r").read().split("\n")

setup(
    name="paps-realtime",
    version=version,
    description="Realtime browser display plugin for paps",
    long_description="",
    author=__author__,
    author_email=__email__,
    url="https://github.com/the01/paps-realtime",
    packages=[
        "paps_realtime"
    ],
    install_requires=requirements,
    include_package_data=True,
    license=__license__,
    keywords="paps audience participation display browser",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7"
    ]
)
