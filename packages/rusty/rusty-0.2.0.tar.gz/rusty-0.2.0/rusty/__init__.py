# -*- coding: utf-8 -*-
'''
Rusty is a collection of extensions (directives and roles)
for `Sphinx documentation framework <http://sphinx.pocoo.org/>`_. While
the extensions are somewhat compatible with `docutils <http://docutils.sourceforge.net>`_,
the usage of *Sphinx is currently required*.

.. contents::

Features
========

At the moment, the Rusty contains following extensions:

**rolelist**
  Generates list from the selected set of role entires,
  written into document. This might come handy for example
  with release notes where bug entries (marked with role syntax)
  are listed automatically::

    Bug fixes
    =========
    Following bugs are fixed in this release:

    .. rolelist:: bug
       :levelsup: 1
       :template: #${value}: ${text}
       :siblings:

    Changes
    =======
    This section lists down all the changes gone in the current release:

    * Fixed :bug:`application crashes <235>` -issue
    * Fixed :bug:`application fails to load document <236>` -issue
    * Fixed :bug:`523`: typos in the documentation
    * Added support for python 2.6, this fixes the :bug:`140`
    * Improved the performance


**includesh**
  Includesh (or include shell) extends the basic functionality of
  ``include`` directive: instead of just including the contents of the
  file into document, the includesh transforms the shell comments into
  documents and commands into literal blocks::

    This section lists down the installation step from the setup.sh:

    .. includesh:: setup.sh

Installation
============
The easiest way to install the package is to use easy_install::

  easy_install -U rusty

Alternative method is to download the package manually, extract it and
install it using traditional methods::

  sudo python setup.py install

Documentation
=============
Documentation provides further information and examples how to use the module.
There exists two resources:

* `Official documentation <http://packages.python.org/rusty>`_
* `Nightly build from trunk <http://jmu.koodiorja.com/projects/rusty>`_

'''
__docformat__ = 'restructuredtext'
__version__ = '0.2.0'
__author__ = 'Juha Mustonen'
__email__ = 'juha,p,mustonen(a)gmail.com'
__license__ = 'MIT'

