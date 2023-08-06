About the CMIS Python Library
=============================
The goal of this project is to create a CMIS client for Python that can be used to work with any CMIS-compliant repository.

The library is being developed with the following guidelines:
 * Developers using this API should be able to work with CMIS domain objects without having to worry about the underlying implementation details.
 * The library will use the Resftul AtomPub Binding.
 * The library will conform to the `CMIS spec <http://docs.oasisopen.org/cmis/CMIS/v1.0/cd04/cmis-spec-v1.0.pdf>`_. As the current Apache Chemistry test server fails the Apache Chemistry TCK, Alfresco will be used as the primary test repository. 
 * The library should have no hard-coded URL's. It should be able to get everything it needs regarding how to work with the CMIS service from the CMIS service URL response and subsequent calls.
 * There shouldn't have to be a vendor-specific version of this library. The goal is for it to be interoperable with CMIS-compliant providers.

Example
-------
This should give you an idea of how easy and natural it is to work with the API:
  >>> cmisClient = CmisClient('http://localhost:8080/alfresco/s/cmis', 'admin', 'admin')
  >>> repo = cmisClient.getDefaultRepository()
  >>> rootFolder = repo.getRootFolder()
  >>> children = rootFolder.getChildren()
  >>> newFolder = rootFolder.createFolder({'cmis:name': 'testDeleteFolder folder'})
  >>> props = newFolder.getProperties()
  >>> newFolder.delete()

.. note::
   I realize the createFolder call currently fails the "hide CMIS details from the user" directive.

To-Do's
-------
The library is not currently production ready. There are many outstanding todo's:
 * Updating a private working copy (PWC) with a file
 * Allowable actions
 * More/better error-handling
 * Implementing optional arguments/filters, paging
 * Type object methods
 * Relationships, Policies, ACLs
 * More/better unit tests
 * Testing against multiple repositories