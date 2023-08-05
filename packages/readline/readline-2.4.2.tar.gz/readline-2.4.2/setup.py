#!/usr/bin/env python

import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, Extension

VERSION = '2.4.2'
DESCRIPTION = "readline extension for Python"
LONG_DESCRIPTION = """
Some platforms, such as Mac OS X, don't ship a working readline extension.

This is the readline extension from Python 2.4.2, built statically against
readline 5.1
"""

CLASSIFIERS = filter(None, map(str.strip,
"""                 
Environment :: Console
Intended Audience :: Developers
License :: OSI Approved :: GNU General Public License (GPL)
Natural Language :: English
Operating System :: MacOS :: MacOS X
Programming Language :: Python
Topic :: Software Development :: Libraries :: Python Modules
""".splitlines()))

LIB = 'readline-darwin-8.3-static/libreadline.a'
setup(
    name="readline",
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    classifiers=CLASSIFIERS,
    author="Bob Ippolito",
    author_email="bob@redivi.com",
    url="http://www.python.org/",
    license="GPL License",
    platforms=['MacOS X'],
    ext_modules=[
        Extension("readline", ["Modules/readline.c"],
            include_dirs=['.'],
            libraries=['curses'],
            extra_link_args=[LIB]
        ),
    ],
    zip_safe=False,
)
