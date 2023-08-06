#!/usr/bin/env python

from setuptools import setup, find_packages
setup(
    name = "tags",
    version = "0.0.2",
    author = "Patrick Sabin",
    author_email = "patricksabin@gmx.at",
    url = "http://pypi.python.org/pypi/tags",
    packages = ["tags"],
    description = "A toolkit to create HTML code with python",
    long_description = open('description.rst', 'r').read(),
    classifiers = [
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Markup :: HTML" ,
        "Programming Language :: Python",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Development Status :: 2 - Pre-Alpha"
    ],
)