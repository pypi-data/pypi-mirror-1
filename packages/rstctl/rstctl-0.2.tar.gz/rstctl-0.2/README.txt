.. contents::

Description
===========

`rstctl` is a script to help you with reStructuredText_

Usage
=====

HTML preview
------------

You can preview a file::

  $ rstctl -w path/to/file.rst

Or the long description of a package::

  $ ls setup.py
  setup.py

  $ rstctl -w

Check links
-----------

You can use the `-l` option to add unknown references to the end of a document.
Example::

  $ cat README.txt 
  Title
  =====

  `incomplete ref`_

  $ ./bin/rstctl -l README.txt 
  <string>:4: (ERROR/3) Unknown target name: "incomplete ref".


  .. _incomplete ref: 


  1 links append to README.txt
  $ cat README.txt 
  Title
  =====

  `incomplete ref`_


  .. _incomplete ref: 

Then you can add the correct links.

.. _reStructuredText: http://docutils.sourceforge.net/rst.html

