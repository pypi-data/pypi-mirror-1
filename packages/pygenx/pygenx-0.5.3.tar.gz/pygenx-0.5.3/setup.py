#
# Copyright (c) 2004 Michael Twomey
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
# KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

"""Wrapper for the genx lightweight canonical XML generation library.

Genx is a light weight C library for the sole purpose of generating
canonical XML. It is simple to use and gaurantees correctness. It operates
purely in UTF-8 and is careful to escape strings when required by the XML or
canonical XML spec.
"""
doclines = __doc__.split("\n")

classifiers = """\
Development Status :: 4 - Beta
Intended Audience :: Developers
License :: OSI Approved :: MIT License
Natural Language :: English
Operating System :: MacOS :: MacOS X
Operating System :: Microsoft :: Windows
Operating System :: POSIX :: Linux
Programming Language :: C
Programming Language :: Python
Topic :: Software Development :: Libraries :: Python Modules
Topic :: Text Processing :: Markup :: XML
"""

from distutils.core import setup
from distutils.extension import Extension
import os
import sys

#Fix this distutils setup.py on older pythons
if sys.version_info < (2, 3):
    _setup = setup
    def setup(**kwargs):
        if kwargs.has_key("classifiers"):
            del kwargs["classifiers"]
        _setup(**kwargs)


setup(
    name = "pygenx",
    version = "0.5.3",
    author = "Michael Twomey",
    author_email = "mick@translucentcode.org",
    url = "http://software.translucentcode.org/pygenx",
    download_url = "http://software.translucentcode.org/pygenx/pygenx-0.5.3.tar.gz",
    license = "http://software.translucentcode.org/pygenx/LICENSE",
    platforms = ["any"],
    description = doclines[0],
    long_description = "\n".join(doclines[2:]),
    classifiers = filter(None, classifiers.split("\n")),
    ext_modules = [
        Extension(
            "genx._genx",
            ["genx/_genx.c"],
        )
    ],
    libraries = [
        ('genx',
            {
                'sources': ["genx/genx.c", "genx/charProps.c"],
            }
        )
    ],
    packages = [
        "genx",
    ],
)

#arch-tag: 7d4122da9e1a4b88976d461a7a3298b1  setup.py.template
# vim:syntax=python:et:ts=4 sw=4

