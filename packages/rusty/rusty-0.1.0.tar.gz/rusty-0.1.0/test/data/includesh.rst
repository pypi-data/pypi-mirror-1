=========
Includesh
=========
Test document for includeshell directive.


Normal usage
============

.. includesh:: script.sh

Inclusion
=========
Should show only the 'it works' -part.

.. includesh:: script.sh
   :start-after: <echo>
   :end-before:  </echo>
