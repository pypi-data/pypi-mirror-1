=====================
 General Information
=====================

.. include:: <isonum.txt>

.. sidebar:: A Brief Historical Note
   :subtitle: Is this software part of Project Xanadu\ |trade|?

   `Project Xanadu`_\ |trade| is a trademark and project of `Ted Nelson`_.
   This software is an independent derivation from the C source of the Xanadu\
   |trade| 88.1 version (renamed to `Udanax Green`_) of that project,
   simplified by taking advantage of the power of Python in representing
   tuples and infinite-precision integers.  Tumblers are a generally useful
   tool.

   .. _`Project Xanadu`: http://www.xanadu.com/
   .. _`Ted Nelson`: http://en.wikipedia.org/wiki/Ted_Nelson
   .. _`Udanax Green`: http://www.udanax.com/green/index.html

.. contents::


Setting Up for Development
**************************

::

  $ svn co https://www.taupro.com/pubsvn/Projects/Xanalogica/xanalogica.tumbler/trunk  xanalogica.tumbler
  $ cd xanalogica.tumbler
  $ python2.5 bootstrap.py
  $ bin/buildout
  $ bin/test

Abstract
********

The xanalogica.tumbler package implements a basic one-dimensional coordinate
type for xanalogical storage systems.  It is useful as keys in mappings and
B-trees, including xanalogical enfilades.  It is written purely in Python but
there are old versions written in C that may be resurrected as 'cTumbler' if
more performance is needed.

.. epigraph::

   Our Kingdom is already twice the size of Spain, and every day we drift
   makes it bigger.

   -- The Kaiser in Werner Herzog's film, "Aguirre, The Wrath of God"
