.. Softwarefabrica django drilldown documentation master file, created by
   sphinx-quickstart on Wed Sep 16 19:50:12 2009.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Softwarefabrica django drilldown documentation!
==========================================================

Contents:

.. toctree::
   :maxdepth: 2

   overview
   install
   views
   templates

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Introduction
============

This `Django`_ application provides the ability to navigate through a large
number of database objects using a `drill down`_ approach, by progressively
refining the set selecting filter values for model fields.

This provides a great alternative to classic search, especially for large
datasets and in those cases where search criterions are not perfectly clear
up-front.

Please refer to the :doc:`overview <overview>` and the :doc:`views <views>`
documents.

Happy coding!

.. _`Django`: http://www.djangoproject.com
.. _`drill down`: http://en.wikipedia.org/wiki/Drill_down
