.. :tabSize=2:indentSize=2:noTabs=true:

.. _rolelist:

================================================================
:mod:`rusty.rolelist` -- List document roles
================================================================
.. module:: rolelist
   :platform: Unix, Windows
   :synopsis: List RST document roles in a bullet list
.. moduleauthor:: Juha Mustonen

.. contents::

Features
========
Rolelist :term:`directive` provides a generic way to list :term:`role` entries from
current document. While it may not sound interesting, consider following
use cases:

.. _rolelist-example:

Changelog
  This use case happens to be initial reason for writing the directive. Consider
  the changelog/relese notes document, containing a list of new features, bug fixes
  and other changes. By using a role, each change can be separated for each other,
  by listing them in a separate list:
  
    .. code-block:: rst
    
      =============
      Release Notes
      =============
      
      Release X
      =========
      Following issues have been fixed in this release:
      
      Fixes
        .. rolelist:: bug
           :template: #${value}: ${text}
           :levelsup: 2
           :siblings:
      
      New features
        .. rolelist:: feat
           :levelsup: 2
           :siblings:
        
        
      All changes 
      -----------
      * Implemented the requested feature :feat:`Support for python 2.6 <235>`
      * :feat:`Added support for MacOS`
      * Fixed issue :bug:`285`
      * Fixed issue :bug:`Crash on start-up <284>`

  .. NOTE::
     The ``bug`` and ``ref`` used in the example are not part of the Sphinx nor
     docutils but custom roles. These and similar definitions can be added in 
     Sphinx :file:`conf.py`:
     
     .. code-block:: python
     
        def setup(app):
          app.add_description_unit('bug', 'bug',
            'pair: %s; Defect')
      
      
Usage
=====
The complete syntax for the directive:

.. code-block:: rst

  .. rolelist:: [role-name]
     :template:   [optional, with string value]
     :docwide:    [optional, set to list roles from non-nested sections - no value]
     :levelsup:   [optional, set with integer how high to climb in document tree]
     :siblings:   [optional, controller option to leave out the sibling nodes 
                   when looking for role entries. The option *has no value* and
                   siblings are *leave out by default*]
     
Which breaks down as follows:     
    
role-name 
  ``required, string value``
  
  Name of the role entries that are wanted to be listed in the bullet list.
  :ref:`See example <rolelist-example>`
   
template
  ``optional, string value``
  
  String template is used for formatting the bullet list items texts. 
  The supported keywords are:
  
  * **value**: The contents between ``''`` or ``<>``
  * **text**: The contents of ``:role:'this if key is defined <key>'``
  
  The keywords are marked with notation: ``$keyword`` or ``${keyword}``.
  The following example is the default template, as the *option is optional*::
    
    ${text} (${value})
    
  For example with ``:file:`` roles you might want to use following template
  instead of the default one:
  
  .. code-block:: rst
    
    .. rolelist:: file
       :template: $text
     
docwide
   ``optional, no value``
   
   A option flag to search only in nested sections or thorough the whole 
   document. The flag is **optional**, and the default value is ``False``.

   .. IMPORTANT::
      If the directive is in section and docwide is disabled, it cannot
      see the roles from sibling section - only nested.
      
levelsup
   ``optional, positive integer``

   Levelsup is an option that controls where to retrieve the roles - or how
   many steps to take up in the document tree nodes, to be exact. The allowed
   value is positive integer (>= 1) and *default value is 0*. All the nested 
   nodes are always visited when searching for roles.
   
   .. NOTE::
      If the value for the 
      ``levelsup`` is very high, the endresult is the same as with ``docwide``
      option.
   
   To get the idea from the option, let's see the example. 
   The ``levelsup`` options is required as the values are separate section:
   
   .. code-block:: rst
     
     Bug fixes
     =========
     
     .. rolelist:: rolename
        :levelsup: 1
        :template: #${value}: ${text}
        :siblings:
     
     Changes
     =======
     
     * Fixed :bug:`application crashes <235>` -issue
     * Fixed :bug:`application fails to load document <236>` -issue
     
siblings
   ``optional, no value``

   controller option to take in the sibling nodes when looking for role entries. 
   The option *has no value* and siblings are left out *by default*. Example:
   
   .. code-block:: rst
     
     Title
     =====
     
     Section A
     ---------
     The contents from next section are taken in now that ``siblings`` flag
     is set.
     
     .. rolelist:: role
        :levelsup: 1
        :siblings:
     
     
     Section B
     ---------
     These entries are found:
     
     * :role:`x`
     * :role:`y`
     * :role:`z`
     
     
       
.. NOTE::

   Rolelist can find the roles only for the current document - i.e. the documents
   included by Sphinx doctree *are not covered*. However, the documents imported
   by the ``include`` directive are read.
   
   If the generated list is empty, the translatable string for having
   "No entries" item is generated in the list.
   
.. TIP::
   Finding a suitable selector (using options like ``levelsup`` and ``siblings``)
   is sometimes a work of trial and error. This is due the node structure of
   the docutils.
   
   In a case you don't get any results into list, try following:
   
   #. Set ``siblings`` option to directive
   #. Try increasing the number in ``levelsup`` option
   


Module in detail
================
  
.. automodule:: rusty.rolelist

.. autoclass:: rusty.rolelist.RoleListNode

.. autoclass:: rusty.rolelist.RoleListDirective
   :members:

.. automethod:: rusty.rolelist.process_rolelist

.. automethod:: rusty.rolelist.setup

