#
# Copyright (c) 2004,2005 Michael Twomey
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


import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages, Extension

version = "0.6"

setup(
    name = "pygenx",
    version = version,
    author = "Michael Twomey",
    author_email = "mick@translucentcode.org",
    url = "http://software.translucentcode.org/pygenx",
    download_url = "http://software.translucentcode.org/pygenx/pygenx-%s.tar.gz" % version,
    license = "http://software.translucentcode.org/pygenx/LICENSE",
    platforms = ["any"],
    description = doclines[0],
    long_description = "\n".join(doclines[2:]),
    classifiers = filter(None, classifiers.split("\n")),
    ext_modules=[ 
        Extension("genx/_genx", [
            "genx/_genx.pyx",
            "src/genx/charProps.c",
            "src/genx/genx.c",
            ],
            include_dirs = ["src/genx",],
        )
    ],
    packages = find_packages(),
)

