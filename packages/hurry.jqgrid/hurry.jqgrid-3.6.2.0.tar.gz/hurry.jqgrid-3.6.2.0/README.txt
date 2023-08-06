hurry.jqgrid
************

Introduction
============

This library packages the jQuery `jqgrid plugin`_ for
`hurry.resource`_ (for jquery).

.. _`hurry.resource`: http://pypi.python.org/pypi/hurry.resource
.. _`jqgrid plugin`: http://www.trirand.com/blog/

How to use?
===========

You can import a variety of jqgrid resources from ``hurry.jqgrid``::

  from hurry.jqgrid import locale_en, grid_base

  .. in your page or widget rendering code, somewhere ..

  locale_en.need()
  grid_base.need()

**Important**: Load a locale *before* you load any grid functionality;
if you don't you will get errors about ``jgrid.format``.

This requires integration between your web framework and
``hurry.resource``, and making sure that the original resources are
published to some URL.

The package has already been integrated for Grok_ and the Zope
Toolkit. If you depend on the `hurry.zoperesource`_ package in your
``setup.py``, the above example should work out of the box. Make sure
to depend on the `hurry.zoperesource`_ package in your ``setup.py``.

.. _`hurry.zoperesource`: http://pypi.python.org/pypi/hurry.zoperesource

.. _Grok: http://grok.zope.org
