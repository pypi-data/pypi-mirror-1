******************************************
:mod:`repoze.slicer` -- Slicing HTML pages
******************************************

:Author: Simplon / Wichert Akkerman
:Version: |version|

.. module:: repoze.slicer
  :synopsis: Sliching HTML pages

.. topic:: Overview

   :mod:`repoze.slicer` is a simple piece of WSGI middleware that can
   extract part of a HTML response. This can be used to reduce the
   amount of parsing and manipulation of DOM trees in browsers, which
   is especially expensive with older versions of IE.


Overview
========

.. toctree::
   :maxdepth: 2

   narr


Change History
==============

.. toctree::
   :maxdepth: 2

.. include:: ../CHANGES.txt


Contacting
==========

The `repoze-dev maillist
<http://lists.repoze.org/mailman/listinfo/repoze-dev>`_ should be used
for communications about this software.


Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
