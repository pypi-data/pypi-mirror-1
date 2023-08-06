#!/bin/sh
      
# Installation phases
#
# 1. Download
# 2. Install
# 3. Configure

# Create temp directory
CDATE=$(date)
mkdir -P /tmp/$CDATE

uptime

# Download the package and locate it to temp directory.
# Finally, extract the package.
#
# Separate line
cd /tmp/$CDATE
wget http://server.com/downloads/package.tar.gz
tar -xzf package.tar.gz

# .. important::
#
#    In case of upgrade, delete the temporary files.
#

##
## Double comment, should not be shown
## 

# 1. Ordered list
# #. Next, test the start-after, end-before parameters

# <echo>
echo "it works"
# </echo>


