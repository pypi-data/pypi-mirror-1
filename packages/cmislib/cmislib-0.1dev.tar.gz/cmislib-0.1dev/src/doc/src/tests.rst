.. _tests:

=====
Tests
=====

This code includes unit tests. To run the tests::

   cd /path/to/cmislib/tests
   Edit cmislibtest.py
   Set REPOSITORY_URL, USERNAME, PASSWORD
   python cmislibtest.py

.. note::
   http://cmis.alfresco.com is a freely-available, hosted CMIS service. If you want to use that for testing, the URL is http://cmis.alfresco.com/s/cmis and the username and password are admin/admin.

If everything goes well, you should see::

   Ran X tests in 3.607s

   OK

.. note::
   Until the entire API is implemented, you may see a number of failures instead of 'OK'.
