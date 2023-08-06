# Copyright (c) 2007-2008 The PyAMF Project.
# See LICENSE for details.

#from ez_setup import use_setuptools

#use_setuptools()

from setuptools import setup, find_packages
from setuptools.command import test

class TestCommand(test.test):
    def run_twisted(self):
        from twisted.trial import runner
        from twisted.trial import reporter

        from pyamf.tests import suite

        r = runner.TrialRunner(reporter.VerboseTextReporter)
        r.run(suite())

    def run_tests(self):
        import logging
        logging.basicConfig()
        logging.getLogger().setLevel(logging.CRITICAL)
        try:
            import twisted

            self.run_twisted()
        except ImportError:
            test.test.run_tests(self)

import sys

#install_requires = ["pywebkitgtk"]
install_requires = []

keyw = """\
"""

setup(name = "Pyjamas-Desktop",
    version = "0.0",
    description = "Pyjamas Widget API for Desktop applications, in Python",
    long_description = open('README', 'rt').read(),
    url = "http://pyamf.org",
    author = "The Pyjamas Desktop Project",
    author_email = "lkcl@lkcl.net",
    keywords = keyw,
    scripts = ["bin/pyjamas.py"],
	packages=["Pyjamas"],
    install_requires = install_requires,
    #test_suite = "pyamf.tests.suite",
    zip_safe=True,
    license = "Apache Software License",
    platforms = ["any"],
    cmdclass = {'test': TestCommand},
    classifiers = [
        "Development Status :: 4 - Beta",
        "Natural Language :: English",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python"
    ])
