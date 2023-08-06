
.. _xmltable:

===========================================
:mod:`rusty.xmltable` -- XMLTable directive
===========================================
.. module:: xmltable
   :platform: Unix, Windows
   :synopsis: Query XML documents into rST tables using :module:`rusty.table`
.. moduleauthor:: Juha Mustonen

.. IMPORTANT::
   Module is in development and not yet ready for general consumption.

Usage
=====

The usage itself is very simple.

.. code-block:: rst

    This is an example rst-document

    .. xmltable::
       :file: foo.xml

       actions/action


    * list
    * item

    And so on..

As it can be seen from the example, there are few ...

file
  relative path to resource XML file

url
  URL to the resource XML. Either this or ``file`` needs to defined.
  
  
Module in detail
================
  
.. automodule:: rusty.xmltable

.. autoclass:: rusty.xmltable.XMLTable

.. autoclass:: rusty.xmltable.XMLTableDirective
