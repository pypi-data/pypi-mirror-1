
.. _includesh:

================================================================
:mod:`rusty.includesh` -- Include shell scripts in documentation
================================================================
.. module:: includesh
   :platform: Unix, Windows
   :synopsis: Easy inclusing of shell script into documentation
.. moduleauthor:: Juha Mustonen

Module extends the standard `include`_ directive by making it
possible to include shell scripts into documents, while providing following
features listed below. See :ref:`includesh-usage` for detailed example
how to use the extension.


.. contents::

Features
========

**Format conversion**
  Given shell file is converted into RST format using following rules:
  
  * Shell commands are turned into code-blocks, using bash highlight
  * Comments are turned into RST format, allowing standard formating rules

**Inclusion**
  Only partial inclusion is supported by providing options:
    
  * *start-after*: text to find in the external data file
    Only the content after the first occurrence of the specified text will be included.
    
  * *end-before*: text to find in the external data file
    Only the content before the first occurrence of the specified text (but after any after text) will be included.
    
  * *encoding*: name of text encoding
    The text encoding of the external data file. Defaults to the document's encoding (if specified). 

**Exclusion**
  Lines starting with double-comment character in shell file are skipped
  while converting to document

.. NOTE::
   * Configuration parameter ``file_insertion_enabled`` *must not be
     disabled* in order to use this directive.
   * Do not put the inclusion flags (``start-after``, ``end-before``)
     after the double-comment characters, as they won't be recognized.

.. _includesh-usage:

Usage
=====
The usage of the extension can be described best by showing 
a real world example:

  Software installation consists from several steps of shell
  commands - which are described in documentation, one by one. 
  However, to prevent user to run same installation steps manually,
  one could create a complete shell script from the installations steps.
  
  While easy-to-run script is nice, the user ends up running the script blindfolded - 
  without actually knowing what is happening as part of the installation process.
  Thus, to increase the knowledge about the software, it would be good to 
  have the actual steps documented as well. Having same steps duplicated in
  script and documents leads eventually in out-dated material.
  
This directive helps to get best parts from both: having up-to-date setup script
AND documentation. By generating the documentation from the script - and here's 
how:

**Shell script: setup.sh**
  Consider having shell script, that is used for example as 
  part of the installation process.
  

  .. literalinclude:: example/setup.sh
     :language: bash
     
     
**Document: document.rst**
  In the documentation, the shell script can be included as a 
  part of the documentation, by using ``includesh`` directive.
  The path to script is relative to the document.
    
  .. literalinclude:: example/document.rst
     :language: rst

     
**Output**
  When the document is processed, the output is shown as follows
  (compare the output with ``setup.sh`` script and ``document.rst``):
  
    .. include:: example/document.rst
    
  
Module in detail
================
  
.. automodule:: rusty.includesh

.. autoclass:: rusty.includesh.IncludeShellDirective

.. autoclass:: rusty.includesh.ShellConverter

.. _`include`: http://docutils.sourceforge.net/docs/ref/rst/directives.html#including-an-external-document-fragment
