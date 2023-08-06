Installation
============

Requirements
------------
These requirements must be met:
 - Python 2.6.x
 - CMIS provider compliant with CMIS 1.0 Committee Draft 04
 
   - Alfresco 3.2r2 (`Download <http://wiki.alfresco.com/wiki/Download_Alfresco_Community_Network>`_)

Steps
-----
The plan is to get this packaged with setuptools. Until then, checkout the source, then copy the src/cmislib directory into a directory that is on your Python lib path such as site-packages.

Once you do that, you should be able to fire up Python on the command-line and import cmislib successfully.

  >>> from cmislib.model import CmisClient, Repository, Folder

To validate everything is working, run some :ref:`tests`.