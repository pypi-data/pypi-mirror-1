#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import sys

import ez_setup
ez_setup.use_setuptools()
from setuptools import setup

from pdfsplit import __version__, __date__, __license__, __author__


setupCommand = sys.argv[-1]


# test before building/installing

if setupCommand == "test":
    print "running test suite"
    cmd = "%s test_pdfsplit.py" % sys.executable
    os.system(cmd)
    sys.exit()


# try converting README from ReST to HTML, if Docutils is installed
# (else issue a warning)

if setupCommand in ("sdist", "build"):
    toolName = "rst2html.py"
    res = os.path.join(os.path.dirname(sys.executable), toolName)
    if os.path.exists(res):
        cmd = "%s '%s' '%s'" % (res, "README.txt", "README.html")
        print "running command %s" % cmd
        cmd = os.system(cmd)
    else:
        print "Warning: No '%s' found. 'README.{txt|html}'" % toolName,
        print "might be out of synch."


# description for Distutils to do its business

long_description = """\
`Pdfsplit` (formally named `pdfslice`) is a Python command-line tool 
and module for splitting and rearranging pages of a PDF document. 
Using it you can pick single pages or ranges of pages from a PDF document 
and store them in a new PDF document. To do this you describe these pages 
with the simple Python slice notation, e.g. ``0:10`` for the first ten 
pages, ``-10:0`` for the last ten pages, ``0::2`` for all even pages, 
``-1::-1`` for all pages in reversed order, etc.

Basically, `pdfsplit` wrapps `pyPdf <http://pypi.python.org/pypi/pyPdf>`_, 
a package written by Mathieu Fenniak which contains the needed 
functionality in its core, but does not provide a simple method of 
using it easily from the command-line or from a Python module.


Features
++++++++

- save arbitrary slices of a given PDF document in a new PDF document
- install a Python module named ``pdfsplit.py``
- install a Python command-line script named ``pdfsplit``
- specify arbitrary slices using Python notation, e.g. ``0:10:2``
- specify pages using normal page numbers (starting at 1), e.g. ``-p 1-5``
- allow patterns for output files
- provide a Unittest test suite


Examples
++++++++

You can use `pdfsplit` as a Python module e.g. like in the following
interactive Python session::

    >>> from pdfsplit import splitPages
    >>>
    >>> splitPages("file.pdf", [slice(0, 1, None)])    # i.e. [0]
    written: file-split.pdf
    >>> splitPages("file.pdf", [slice(None, None, 2)]) # i.e. [::2] 
    written: file-split.pdf

In addition there is a script named ``pdfsplit``, which can be used 
more easily from the system command-line like this (you can see many 
more examples when typing ``pdfsplit -h`` on the command-line)::

    $ pdfsplit 0 file.pdf
    written: file-split.pdf
    $ pdfsplit ::2 file.pdf
    written: file-split.pdf
    $ pdfsplit -p -o "%(dirname)s/%(base)s-p%(indices)s%(ext)s" 3-5 file.pdf  
    written: file-p3-5.pdf
"""


classifiers = [
    "Development Status :: 4 - Beta",
    "Environment :: Console",
    "Intended Audience :: End Users/Desktop",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: GNU General Public License (GPL)",
    "Operating System :: MacOS :: MacOS X",
    "Operating System :: POSIX",
    "Operating System :: Microsoft :: Windows",
    "Programming Language :: Python",
    "Topic :: Utilities",
    "Topic :: Printing",
]

baseURL = "http://www.dinu-gherman.net/"

setup(
    name = "pdfsplit",
    version = __version__,
    description = "Split a PDF file or rearrange its pages into a new PDF file.",
    long_description = long_description,
    date = __date__,
    author = __author__,
    author_email = "@".join(["gherman", "darwin.in-berlin.de"]),
    maintainer = __author__,
    maintainer_email = "@".join(["gherman", "darwin.in-berlin.de"]),
    license = __license__,
    platforms = ["Posix", "Windows"],
    keywords = ["PDF", "slicing pages", "rearraging pages"],
    url = baseURL,
    download_url = baseURL + "tmp/pdfsplit-%s.tar.gz" % __version__,
    py_modules = ["pdfsplit"],
    scripts = ["pdfsplit"],
    classifiers = classifiers,

    # for setuptools, only
    install_requires = ["pyPdf>1.10"],
)
