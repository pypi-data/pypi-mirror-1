
Installation phases

1. Download
2. Install
3. Configure

Create temp directory

.. code-block:: bash

   CDATE=$(date)
   mkdir -P /tmp/$CDATE

   uptime


Download the package and locate it to temp directory.
Finally, extract the package.

.. code-block:: bash

   cd /tmp/$CDATE
   wget http://server.com/downloads/package.tar.gz
   tar -xzf package.tar.gz  
