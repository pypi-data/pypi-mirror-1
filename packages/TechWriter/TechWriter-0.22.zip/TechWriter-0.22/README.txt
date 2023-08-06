=========================
TechWriter Python Package
=========================

:Author: `David Boddie`_
:Date: 2008-07-13
:Version: 0.22

*Note: This text is marked up using reStructuredText formatting. It should be
readable in a text editor but can be processed to produce versions of this
document in other formats.*


.. contents::


Introduction
------------

TechWriter_ is a mathematical word processor for the RISC OS platform that
encourages authors to write documents in a structured style. Unlike other
word processors, in which chapters and sections are created by inserting
styled text in the appropriate places to create headings, TechWriter documents
are collections of nested objects, representing chapters, sections, figures
and other elements.

Although this structured, object-based approach is ideal for certain kinds of
documents and resembles other document creation systems, it is not easy to
convert documents stored in TechWriter's file format to file formats for use
with systems such as LaTeX_ and LyX_. TechWriter can export documents as TeX_
files, but this process doesn't export all the information that some users
require, it can produce TeX markup that isn't suitable for re-use, and it
requires that the document's author is able to use TechWriter to perform the
conversion.

This package aims to help those who want to convert documents written using
TechWriter to other formats, extracting their contents reliably and as
accurately as possible, by providing a package and some tools for use with the
Python_ programming language.


The TechWriter Package
----------------------

A Python package is provided that provides facilities for reading TechWriter
format files (filetype D01 on RISC OS) and extracting information about its
structure and contents.

* The ``document`` module contains the ``Document`` class that is used to
  read TechWriter files and store information about their contents.
* The ``maths`` and ``text`` modules contain classes that encapsulate
  information about mathematical notation and textual effects.
* The ``objects`` module contains classes to represent document structures.
* The ``Writers`` package provides simple implementations of writers for HTML,
  LaTeX and OpenDocument Text formats, as well as a writer that creates a
  summary in HTML of the contents of a document.


Requirements
------------

The OpenDocument Text writer depends on the odfpy_ package. This can be
installed separately using the instructions given in the documentation for
that package.


Installation
------------

To install the package alongside other packages and modules in your Python
installation, unpack the contents of the archive. At the command line, enter
the directory containing the ``setup.py`` script and install it by typing the
following::

  python setup.py install

You may need to become the root user or administrator to do this.


Tools
-----

Currently, the following convertor tools are provided in the ``Tools``
directory. These read TechWriter files and write out one or more files in
the appropriate formats. Tools that use the ``TechWriter`` package are
expected to be minimal wrappers around the features of the writer modules
they use.

* ``tw2latex.py`` writes files containing LaTeX markup.
* ``tw2html.py`` writes HTML files.
* ``tw2odt.py`` writes files in OpenDocument Text format, suitable for
  reading in OpenOffice.org.


License
-------

The contents of this package are licensed under the GNU General Public License
(version 3 or later)::

 TechWriter, a Python package for reading and converting TechWriter documents.
 Copyright (C) 2007 David Boddie <david@boddie.org.uk>

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.



.. _TechWriter:     http://www.iconsupport.demon.co.uk/
.. _LaTeX:          http://www.latex-project.org/
.. _LyX:            http://www.lyx.org/
.. _TeX:            http://www.tug.org/
.. _Python:         http://www.python.org/
.. _odfpy:          http://opendocumentfellowship.com/projects/odfpy
.. _`David Boddie`: mailto:david@boddie.org.uk
