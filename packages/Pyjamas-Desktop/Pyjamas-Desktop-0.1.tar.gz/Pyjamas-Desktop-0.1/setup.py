# Copyright (c) 2007-2008 The PyAMF Project.
# See LICENSE for details.

#from ez_setup import use_setuptools

#use_setuptools()

from setuptools import setup, find_packages
from setuptools.command import test

import sys

#install_requires = ["pywebkitgtk"]
install_requires = []

keyw = """\
"""

setup(name = "Pyjamas-Desktop",
    version = "0.1",
    description = "Pyjamas Widget API for Desktop applications, in Python",
    long_description = open('README.txt', 'rt').read(),
    url = "http://pyjs.sf.net",
    author = "The Pyjamas Desktop Project",
    author_email = "lkcl@lkcl.net",
    keywords = keyw,
    scripts = ["bin/pyjd.py"],
	packages=["pyjamas"],
    install_requires = install_requires,
    #test_suite = "pyamf.tests.suite",
    zip_safe=True,
    license = "Apache Software License",
    platforms = ["any"],
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Natural Language :: English",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python"
    ])
