.. _topics-install:

===============================================
How to install Softwarefabrica django drilldown
===============================================

.. admonition:: About this document

   This document describes how to install Softwarefabrica django drilldown and
   use it in your Django applications.

.. contents::
   :depth: 3

.. _pre-requisites:

See also the `documentation index`_.

.. _`documentation index`: index.html

Pre-requisites
==============

This library depends on `softwarefabrica.django.utils`_,
`softwarefabrica.django.forms`_, `softwarefabrica.django.crud`_,
`softwarefabrica.django.common`_ and `sflib`_ from the same author.
If you use EasyInstall_, as outlined below, dependencies will be satisfied
automatically (the ``easy_install`` command will take care of everything).

.. _EasyInstall: http://peak.telecommunity.com/DevCenter/EasyInstall
.. _`softwarefabrica.django.utils`: http://pypi.python.org/pypi/softwarefabrica.django.utils
.. _`softwarefabrica.django.forms`: http://pypi.python.org/pypi/softwarefabrica.django.forms
.. _`softwarefabrica.django.crud`: http://pypi.python.org/pypi/softwarefabrica.django.crud
.. _`softwarefabrica.django.common`: http://pypi.python.org/pypi/softwarefabrica.django.common
.. _`sflib`: http://pypi.python.org/pypi/sflib

.. _installing-official-release:

Installing an official release
==============================

Official releases are made available from PyPI_

http://pypi.python.org/pypi/softwarefabrica.django.drilldown

Binary distribution
-------------------

::

  $ su
  # easy_install softwarefabrica.django.drilldown

If you are using Ubuntu, to install system-wide:

::

  $ sudo easy_install softwarefabrica.django.drilldown

Otherwise, if EasyInstall_ is not available, you can just download (eg. from
PyPI_) the right `distribution`_ for your platform and Python version, extract
it and run the usual ``setup.py`` commands:

::

  $ su
  # python setup.py install

These commands will install the software in your Python installation's
``site-packages`` directory.

.. _EasyInstall: http://peak.telecommunity.com/DevCenter/EasyInstall
.. _PyPI: http://pypi.python.org/pypi
.. _`distribution`: http://pypi.python.org/pypi/softwarefabrica.django.drilldown

.. _`source distribution installation`:

Source distribution
-------------------

If you have EasyInstall_ available, you can download and extract the most
up-to-date source distribution in one step. For example, on a unix-like system:

::

  easy_install --editable --build-directory ~/projects softwarefabrica.django.drilldown

Then from the ``softwarefabrica.django.drilldown`` directory you can run the
``setup.py develop`` command to install the library in your Python
`site-packages` directory using a link, which allows to continue developing
inside the working tree without the need to re-install after every change. See
the `setuptools development mode`_ documention for more information::

    $ python setup.py build
    $ sudo
    # python setup.py develop

Otherwise, if EasyInstall_ is not available, you can just download the `source
distribution`_ (eg. from PyPI_), extract it and run the usual ``setup.py`` commands:

::

  $ su
  # python setup.py install

This command will install the software in your Python installation's
``site-packages`` directory.

.. _EasyInstall: http://peak.telecommunity.com/DevCenter/EasyInstall
.. _PyPI: http://pypi.python.org/pypi
.. _`source distribution`: http://pypi.python.org/pypi/softwarefabrica.django.drilldown
.. _`setuptools development mode`: http://peak.telecommunity.com/DevCenter/setuptools#development-mode


Windows installer
-----------------

A Windows installer will be made available in a next release.

.. _installing-development-version:

Installing the development version
==================================

Alternatively, if you'd like to update the software occasionally to pick
up the latest bug fixes and enhancements before they make it into an
offical release, branch from the `Bazaar`_ repository hosted on `LaunchPad`_
instead.
Just follow the procedure outlined below:

1. Make sure that you have `Bazaar`_ installed, and that you can run its
   commands from a shell. (Enter ``bzr help`` at a shell prompt to test
   this.)

2. Create a local branch and working tree from the official one::

    bzr branch lp:sf-django-drilldown sf-drilldown

3. Then from the ``sf-drilldown`` directory you can run the ``setup.py develop``
   command to install the library in your Python `site-packages` directory
   using a link, which allows to continue developing inside the working tree
   without the need to re-install after every change. See the
   `setuptools development mode`_ documention for more information::

    $ python setup.py build
    $ sudo
    # python setup.py develop

4. You can verify that the application is available on your `PYTHONPATH`_ by
   opening a Python interpreter and entering the following commands::

    >>> from softwarefabrica.django.drilldown import version
    >>> version.VERSION
    (0, 9, 'dev')
    >>> version.get_version()
    u'0.9-dev-BZR-rXX-panta@elasticworld.org-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'

When you want to update your copy of the library source code, run the command
``bzr pull`` from within the ``sf-drilldown`` directory::

    bzr pull
    python setup.py build
    sudo python setup.py develop

(you need to re-run the ``setup.py develop`` command after every working tree
update, to update version numbers in script wrappers).

.. caution::

   The development version may contain bugs which are not present in the
   release version and introduce backwards-incompatible changes.

   If you're tracking trunk, keep an eye on the `changes`_ before you update
   your copy of the source code.

.. _`development home page`: https://launchpad.net/sf-django-drilldown
.. _`bugs`: https://bugs.launchpad.net/sf-django-drilldown
.. _`LaunchPad`: http://launchpad.net
.. _`Bazaar`: http://bazaar-vcs.org/
.. _`changes`: http://bazaar.launchpad.net/~softwarefabrica/sf-django-drilldown/trunk/changes
.. _`PYTHONPATH`: http://docs.python.org/tut/node8.html#SECTION008110000000000000000
.. _`junction`: http://www.microsoft.com/technet/sysinternals/FileAndDisk/Junction.mspx
.. _`setuptools development mode`: http://peak.telecommunity.com/DevCenter/setuptools#development-mode
