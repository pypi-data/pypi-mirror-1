=======
Testing
=======

.. WARNING::

   This page is only for testing purposes - as it is much 
   easier to unit test using eyes and sphinx

.. contents::   

Role: :file:`root`
   

Includesh
=========
Include shell scripts into document, by switching the shell comments into
texts and shell commands into literal blocks.

**Original**

.. include:: ../test/data/script.sh
   :literal:

**Output**

.. includesh:: ../test/data/script.sh

Rolelist
========
Generate lists from document roles.   

List all the files mentioned in this page:

.. rolelist:: file
   :template: $text
   :docwide:

Release X   
---------

Fixes
~~~~~
Refs in changes

.. rolelist:: ref
   :levelsup: 1
   :siblings:

Changes
~~~~~~~
Following listing contains *all the changes* for release X

* :ref:`x1`
* :ref:`x2`
* :ref:`äksä <x3>`


Release Y   
---------
Refs in changes

.. rolelist:: ref

**Nested**

  .. rolelist:: ref
     :template: NESTED: $value
     :levelsup: 1
     :siblings:

Changes
~~~~~~~
Following listing contains *all the changes* for release Y

* :ref:`y1`
* :ref:`y2`
* :ref:`äksy <y3>`

  - Deep down
  
    - In the dungeon
    
      - There lurks the 
      
        - :ref:`Reference dragon <dragon>`

Deep down, there is :file:`subsub`

Release Z
----------
Non-existing item listing.

.. rolelist:: foo

And what about :the: levels. This entry has no ``levelsup`` definition.

.. rolelist:: file

Summary
-------

**Tasks**
    Following tasks were carried out in this release:
    
    .. rolelist:: task
       :template: ${value} (${text})    
       :levelsup: 4
       :siblings:
            
**Defects**
    Following bugs were squashed in this reelease
    
    .. rolelist:: bug
       :template: #${value}
       :levelsup: 4
       :siblings:
       
       
Changes
-------
Following changes are included in the release.

**Component X**

- Fixed :bug:`FOOB-7PLAHR`: Description
- Fixed :bug:`FOOB-7P44GT`: Description
- Fixed :bug:`BARB-7PLFY3`: Description
- Fixed :bug:`BARB-7PLGB4`: Description
- Fixed :bug:`FOOB-7PT5QF`: Description
- Fixed :bug:`BARB-7PUB52`: Description
- Fixed :bug:`FOOB-7Q43ZH`: Description
- Fixed :bug:`BARB-7PTDS5`: Description
- Fixed :bug:`FOOB-7P69C5`: Description
- Fixed :bug:`FOOB-7NVAAL`: Description
- Finisihed :task:`Description <TSK-908>`  

**Component Y**

- Fixed :bug:`BAZ-7PLAHR`: Description
- Fixed :bug:`BAZ-7P44GT`: Description
- Fixed :bug:`HUZ-7PLFY3`: Description
- Fixed :bug:`HUZ-7PLGB4`: Description
- Fixed :bug:`BAZ-7PT5QF`: Description
- Fixed :bug:`HUZ-7PUB52`: Description
- Fixed :bug:`BAZ-7Q43ZH`: Description
- Fixed :bug:`HUZ-7PTDS5`: Description
- Fixed :bug:`BAZ-7P69C5`: Description
- Fixed :bug:`BAZ-7NVAAL`: Description
- Finisihed :task:`Description <TSK-108>` 

Testing :file:`foo` and :file:`Baari <bar>` 



Siblings
--------
Test siblings functionality.


Positive test
~~~~~~~~~~~~~

**Section A**
  The contents from next section are taken in now that ``siblings`` flag
  is set.
  
  .. rolelist:: task
    :levelsup: 2
    :template: $value
    :siblings:


**Section B**
  These entries are found:
  
  * :task:`x`
  * :task:`y`
  * :task:`z`
  
Negative test
~~~~~~~~~~~~~

**Section A**
  The contents from next section are left out since the ``siblings`` flag
  **is not set**.
  
  .. rolelist:: task
    :levelsup: 2
    :template: $value


**Section B**
  These entries are *not supposed to be found*:
  
  * :task:`nx`
  * :task:`ny`
  * :task:`nz`  
