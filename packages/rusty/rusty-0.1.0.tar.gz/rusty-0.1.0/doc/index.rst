======
Rusty
======
.. automodule:: rusty

This is document describes :ref:`how to install <intro>` and :ref:`use <further>` 
the :mod:`rusty` module in question.

.. _features:

Features
========
Following extensions are currently available in the Rusty module. The detailed usage
information for each extension are described in the subsections:


:doc:`includesh <includesh>` (Directive)
  Extends the standard include directive by converting the given shell file
  into RST format: comments are formatted and commands put in code blocks.
  
:doc:`rolelist <rolelist>` (Directive)
  Creates the bullet list from the selected role, with custom string template.

..  
  :doc:`xmltable <xmltable>` (Directive)
    Similar functionality to docutils csv-table: makes it possible to read data
    from XML/HTML file into table easily.
    
    .. WARNING::
       xmltable is currently in the works and does not work yet.

       
.. index:: Installation

.. _intro:

Quick introduction
==================
Here you can find the minimum steps for installation and usage of the module:

#. Install setuptools::
  
     wget peak.telecommunity.com/dist/ez_setup.py
     sudo python ez_setup.py
  
#. `Download the package <http://jmu.koodiorja.com/projects/rusty/>`_,  
   extract the package and install the module::

     tar -xzf rusty-x.y.z.tar.gz
     sudo python setup.py install

   **OR**
   
   Run the command::
     
     easy_install -f http://jmu.koodiorja.com/projects/rusty rusty


#. Install `Sphinx`_::

     sudo easy_install -U Sphinx

#. Start new Sphinx powered documentation project and continue with existing::

     sphinx-quicstart

#. Configure rusty directive or role of your choice into Sphinx :file:`conf.py`
   configuration file. See :ref:`features` for available extensions.

   .. code-block:: python

     # Add ``rusty`` into extension list
     extensions = ['sphinx.ext.autodoc', 'sphinx.ext.doctest', 'rusty.includesh']
     
#. Place directive/role in your document:

   .. code-block:: rst

      My document
      ===========
      The contents of the setup script:

      .. includesh: setup.sh

#. Build the document::
  
     sphinx-build -b html doc dist/html

#. That's it!     

.. _further:

Further information
===================
Interested in module? See following sections for further information about it.

.. toctree::
 
   changelog
   devel
   glossary
   
.. toctree::
   :hidden:
   
   table
   xmltable
   includesh
   global
   rolelist
   test
   
.. include:: global.rst

   
