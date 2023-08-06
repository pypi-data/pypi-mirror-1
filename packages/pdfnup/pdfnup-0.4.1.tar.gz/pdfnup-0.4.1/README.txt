.. -*- mode: rst -*-

========
Pdfnup
========

---------------------------------------------------------------------
Layout multiple pages per sheet of a PDF document.
---------------------------------------------------------------------

:Author:     Dinu Gherman <gherman@darwin.in-berlin.de>
:Homepage:   http://www.dinu-gherman.net/
:Version:    Version 0.4.1
:Date:       2009-07-06
:Copyright:  GNU Public Licence v3 (GPLv3)


About
-----

`Pdfnup` is a Python module and command-line tool for layouting multiple 
pages per sheet of a PDF document. Using it you can take a PDF document 
and create a new PDF document from it where each page contains a number
of minimized pages from the original PDF file. 

Right now `pdfnup` should be used on documents with all pages the same 
size, and half square page numbers per sheet work best on paper sizes
of the ISO A series.

Basically, `pdfnup` wrapps `pyPdf <http://pypi.python.org/pypi/pyPdf>`_, 
a package written by Mathieu Fenniak, which does not provide tools like 
this for using the core functionality easily from the command-line or 
from a Python module. `Pdfnup` itself was much inspired from some code 
written by Henning von Bargen - thanks, Henning!

This release provides full support for file objects and StringIO objects
for input as well as output documents and fixes a nasty buglet in the 
command-line invocation script.


Features
--------

- save minimized pages of a given PDF document in a new PDF document
- place n pages per sheet, with n being square or half square
- customize layout order, both horizontally and vertically
- turn rotated pages to make them all have the same format 
- allow patterns for output files
- supports file-like objects for input and output documents
- install a Python module named ``pdfnup.py``
- install a Python command-line script named ``pdfnup``
- provide a Unittest test suite


Examples
--------

You can use `pdfnup` as a Python module e.g. like in the following
interactive Python session::

    >>> from pdfnup import generateNup
    >>>
    >>> generateNup("file.pdf", 8, verbose=True)
    written: file-8up.pdf
    >>>
    >>> generateNup("file.pdf", 8, dirs="LD", verbose=True)
    written: file-8up.pdf
    >>>
    >>> f = open("file.pdf")
    >>> generateNup(f, 8, outPathPatternOrFile="out-%(n)dup.pdf", verbose=True)
    written: out-8up.pdf

In addition there is a script named ``pdfnup``, which can be used 
more easily from the system command-line like this (you can see 
more examples when typing ``pdfnup -h`` on the command-line)::

    $ pdfnup -V file.pdf
    written: file-4up.pdf
    $ pdfnup -V -n 8 file.pdf
    written: file-8up.pdf
    $ pdfnup -V -n 8 -l LD file.pdf
    written: file-8up.pdf
    $ pdfnup -V -n 9 /path/file[12].pdf  
    written: /path/file1-9up.pdf
    written: /path/file2-9up.pdf
    $ pdfnup -V -n 8 -o "%(dirname)s/foo.pdf" /path/file.pdf
    written: /path/foo.pdf


Installation
------------

There are two ways to install `pdfnup`, depending on whether you have
the `easy_install` command available on your system or not.

1. Using `easy_install`
++++++++++++++++++++++++

With the `easy_install` command on your system and a working internet 
connection you can install `pdfnup` with only one command in a terminal::

  $ easy_install pdfnup

If the `easy_install` command is not available to you and you want to
install it before installing `pdfnup`, you might want to go to the 
`Easy Install homepage <http://peak.telecommunity.com/DevCenter/EasyInstall>`_ 
and follow the `instructions there <http://peak.telecommunity.com/DevCenter/EasyInstall#installing-easy-install>`_.

2. Manual installation
+++++++++++++++++++++++

Alternatively, you can install the `pdfnup` tarball after downloading 
the file ``pdfnup-0.4.1.tar.gz`` and decompressing it with the following 
command::

  $ tar xfz pdfnup-0.4.1.tar.gz

Then change into the newly created directory ``pdfnup`` and install 
`pdfnup` by running the following command::

  $ python setup.py install
  
This will install a Python module file named ``pdfnup.py`` in the 
``site-packages`` subfolder of your Python interpreter and a script 
tool named ``pdfnup`` in your ``bin`` directory, usually in 
``/usr/local/bin``.


Dependencies
------------

`Pdfnup` depends on `pyPdf` which, if missing, will miraculously be 
installed together with `pdfnup` if you have a working internet 
connection during the installation procedure. If for whatever reason 
`pyPdf` cannot be installed, `pdfnup` should still install fine. 
In this case you'll get a warning when trying to run `pdfnup`.

Starting with version 0.3.1 `pdfnup` no longer needs the `ReportLab 
toolkit <http://www.reportlab.org/downloads.html>`_ to be installed, 
except for running the Python script `genpdf.py` generating the 
initial PDF files for the test suite (but even those are included
in the distribution).


Testing
-------

The `pdfnup` tarball distribution contains a Unittest test suite 
in the file ``test_pdfnup.py`` which can be run like shown in the 
following lines on the system command-line::
 
  $ tar xfz pdfnup-0.4.1.tar.gz
  $ cd pdfnup-0.4.1
  $ python test_pdfnup.py
  ...........
  ----------------------------------------------------------------------
  Ran 11 tests in 21.658s

  OK


Bug reports
-----------

Please report bugs and patches to Dinu Gherman <gherman@darwin.in-berlin.de>. 
Don't forget to include information about the operating system and Python 
versions being used.
