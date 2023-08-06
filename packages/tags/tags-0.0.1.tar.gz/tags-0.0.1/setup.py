#!/usr/bin/env python

from setuptools import setup, find_packages
setup(
    name = "tags",
    version = "0.0.1",
    author = "Patrick Sabin",
    author_email = "patricksabin@gmx.at",
    url = "http://pypi.python.org/pypi/tags",
    packages = ["tags"],
    description = "A toolkit to create HTML code with python",
    long_description = """\
Tags - A HTML code generation toolkit
-------------------------------------
With tags you can generate HTML code by programming python. For every Tag type
there is a corresponding class, for every tag an object. This way you can
program HTML code by programmatically coding in python. The advantage of this
style is that you can easily structure and reuse your HTML code, something that
pure HTML is missing. For example, you can create a widget and use it at many
different places, or create a template and plug some other html code in. Tags
takes care of only creating valid html code.

This project is still in development. There is enough code to play around, but
some tags are missing.

This version requires Python 2.
""",
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