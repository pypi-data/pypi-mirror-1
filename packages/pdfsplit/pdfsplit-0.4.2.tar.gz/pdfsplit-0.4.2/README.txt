.. -*- mode: rst -*-

========
Pdfsplit
========

---------------------------------------------------------------------
A tool for splitting and rearranging pages in a PDF document.
---------------------------------------------------------------------

:Author:     Dinu Gherman <gherman@darwin.in-berlin.de>
:Homepage:   http://www.dinu-gherman.net/
:Version:    Version 0.4.2
:Date:       2008-09-17
:Copyright:  GNU Public Licence v3 (GPLv3)


About
-----

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
--------

- save arbitrary slices of a given PDF document in a new PDF document
- install a Python module named ``pdfsplit.py``
- install a Python command-line script named ``pdfsplit``
- specify arbitrary slices using Python notation, e.g. ``0:10:2``
- specify pages using normal page numbers (starting at 1), e.g. ``-p 1-5``
- allow patterns for output files
- provide a Unittest test suite


Examples
--------

You can use `pdfsplit` as a Python module e.g. like in the following
interactive Python session (the function's signature might still change 
a bit in the future)::

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
    $ pdfsplit -p -o "%(base)s-p%(indices)s%(ext)s" 3-5 /path/file[12].pdf  
    written: file1-p3-5.pdf
    written: file2-p3-5.pdf
  

Installation
------------

There are two ways to install `pdfsplit`, depending on whether you have
the `easy_install` command available on your system or not.

1. Using `easy_install`
++++++++++++++++++++++++

With the `easy_install` command on your system and a working internet 
connection you can install `pdfsplit` with only one command in a terminal::

  $ easy_install pdfsplit

If the `easy_install` command is not available to you and you want to
install it before installing `pdfsplit`, you might want to go to the 
`Easy Install homepage <http://peak.telecommunity.com/DevCenter/EasyInstall>`_ 
and follow the `instructions there <http://peak.telecommunity.com/DevCenter/EasyInstall#installing-easy-install>`_.

2. Manual installation
+++++++++++++++++++++++

Alternatively, you can install the `pdfsplit` tarball after downloading 
the file ``pdfsplit-0.4.0.tar.gz`` and decompressing it with the following 
command::

  $ tar xfz pdfsplit-0.4.0.tar.gz

Then change into the newly created directory ``pdfsplit`` and install 
`pdfsplit` by running the following command::

  $ python setup.py install
  
This will install a Python module file named ``pdfsplit.py`` in the 
``site-packages`` subfolder of your Python interpreter and a script 
tool named ``pdfsplit`` in your ``bin`` directory, usually in 
``/usr/local/bin``.


Dependencies
------------

`Pdfsplit` depends on `pyPdf` which, if missing, will miraculously be 
installed together with `pdfsplit` if you have a working internet 
connection during the installation procedure. If for whatever reason 
`pyPdf` cannot be installed, `pdfsplit` should still install fine. 
In this case you'll get a warning when trying to run `pdfsplit`.


Testing
-------

The `pdfsplit` tarball distribution contains a Unittest test suite 
in the file ``test_pdfsplit.py`` which can be run like shown in the 
following lines on the system command-line::
 
  $ tar xfz pdfsplit-0.4.0.tar.gz
  $ cd pdfsplit
  $ python test_pdfsplit.py
  written: samples/test-split.pdf
  .written: samples/test-split-0.pdf
  .written: samples/test-split-0..5.pdf
  .written: samples/test-odd.pdf
  .written: samples/test-reversed.pdf
  ....
  ----------------------------------------------------------------------
  Ran 8 tests in 0.498s

  OK


Bug reports
-----------

Please report bugs and patches to Dinu Gherman 
<gherman@darwin.in-berlin.de>. Don't forget to include information 
about the operating system and Python versions being used.
