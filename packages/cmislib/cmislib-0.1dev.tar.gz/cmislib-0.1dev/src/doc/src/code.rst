Code
====

The :mod:`cmislib.model` Module
-------------------------------

The :mod:`cmislib.model` Module contains all the CMIS domain objects. When working with the repository, the first thing you need to do is grab an instance of :class:`cmislib.model.CmisClient`, passing it the repository endpoint URL, username, and password.

>>> cmisClient = CmisClient('http://localhost:8080/alfresco/s/cmis', 'admin', 'admin')

From there you can get the default repository, or a specific repository if you know the repository ID.

>>> repo = cmisClient.getDefaultRepository()

Once you have that, you're off to the races. Use the :class:`cmislib.model.Repository` class to create new :class:`cmislib.model.Folder` and :class:`cmislib.model.Document` objects, perform searches, etc.

.. automodule:: cmislib.model
   :members:

The :mod:`cmislib.net` Module
-----------------------------

The :mod:`cmislib.net` Module contains the classes used by :mod:`cmislib.model.CmisClient` to communicate with the CMIS repository. The most important of which is :class:`cmislib.net.RESTService`.

.. automodule:: cmislib.net
   :members: RESTService