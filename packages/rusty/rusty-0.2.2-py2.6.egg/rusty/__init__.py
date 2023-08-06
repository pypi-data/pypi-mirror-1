# -*- coding: utf-8 -*-
'''
Rusty is a collection of extensions (directives and roles)
for `Sphinx documentation framework <http://sphinx.pocoo.org/>`_. While
the extensions are somewhat compatible with `docutils
<http://docutils.sourceforge.net>`_,
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


**regxlist**
  Similar to rolelist directive. The main difference is the
  capability to create list based on regular expression rule.

  Example::

    .. IMPORTANT:: Action points

        .. regxlist:: (AP|-->)+\s+(to)*\s*(?P<name>(\w|\s)+):\s*(?P<desc>(\w|\n|\s)*)
           :template: ${name}: ${desc}
           :siblings:
           :levelsup: 2

    - Software building process is still hard, AP Sarah: improve building process
    - AP to Tom: document the building process
    - Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aenean risus mauris,
      ultrices id, pretium sed, lobortis in, nisl. Nunc tincidunt neque vel libero
      hendrerit malesuada.
    - Pellentesque dolor augue, dapibus dictum, elementum quis, tincidunt
      consectetur, nunc. Sed vulputate dolor ut sem. In varius rutrum odio.
    - Release needs to be ready for monday --> Sarah: create official release
    - Nunc sit amet neque sed lorem condimentum interdum. In hac habitasse
      platea dictumst. Vivamus vel libero eget lectus ultrices vestibulum.
    - Blah blah...

**xmltable**
  Similar functionality to csv-table - one of the docutils directives: read data
  from XML/HTML file and convert it to RST-table based on given query and iterator.
  Requires BeautifulSoup -module.

  Example::

    Producing following table:

    .. xmltable:: Animal table caption
         :file: example/animals.xml
         :header: Name, Species, ID
         :query: /zoo/animal

         name
         species
         self@id


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

Changelog
=========

Release 0.2.2 (2009-06-18)
------------------------------
Maintenance release, containing following changes:

* Fixed issue #4 again: paver-minilib.zip is missing from the package

Release 0.2.1 (2009-06-16)
------------------------------
Maintenance release, containing following changes:

* Fixed issue #4: setup.py is missing from the package

Release 0.2.0 (2009-06-01)
------------------------------
Changes since previous release:

* New directive: xmltable
* New directive: regxlist
* Improved unit testing
* Improved building
* Migrated version control from subversion to mercurial
* Published the project in Bitbucket: http://bitbucket.org/jmu/rusty
* Added FAQ

Release 0.1.0 (2009-03-31)
--------------------------
First release, containing following functionality

* New directive: includesh
* New directive: rolelist
* Initial set of unit tests (see testing)
* Paver powered build and release management

'''
__docformat__ = 'restructuredtext'
__version__ = '0.2.2'
__author__ = 'Juha Mustonen'
__email__ = 'juha,p,mustonen(a)gmail.com'
__license__ = 'MIT'

