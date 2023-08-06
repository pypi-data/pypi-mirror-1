About the CMIS Python Library
=============================
The goal of this project is to create a CMIS client for Python that can be used to work with any CMIS-compliant repository.

The library is being developed with the following guidelines:
 * Developers using this API should be able to work with CMIS domain objects without having to worry about the underlying implementation details.
 * The library will use the Resftul AtomPub Binding.
 * The library will conform to the `CMIS spec <http://docs.oasisopen.org/cmis/CMIS/v1.0/cd04/cmis-spec-v1.0.pdf>`_. As the current Apache Chemistry test server fails the Apache Chemistry TCK, Alfresco will be used as the primary test repository. 
 * The library should have no hard-coded URL's. It should be able to get everything it needs regarding how to work with the CMIS service from the CMIS service URL response and subsequent calls.
 * There shouldn't have to be a vendor-specific version of this library. The goal is for it to be interoperable with CMIS-compliant providers.

Quick Example
-------------
This should give you an idea of how easy and natural it is to work with the API:
  >>> cmisClient = CmisClient('http://localhost:8080/alfresco/s/cmis', 'admin', 'admin')
  >>> repo = cmisClient.getDefaultRepository()
  >>> rootFolder = repo.getRootFolder()
  >>> children = rootFolder.getChildren()
  >>> newFolder = rootFolder.createFolder('testDeleteFolder folder')
  >>> props = newFolder.getProperties()
  >>> newFolder.delete()

To-Do's
-------
Miscellaneous
 * createDocumentFromSource
 * getProperties filter
 * refactor property name hack
 * getContentStream stream id
 * Document.move

Renditions
 * getRenditions

Change history
 * getContentChanges
 * change token

Unfiling/multifiling support
 * addObject
 * removeObject
 * createDocument without a parent folder (unfiled)
 * getObjectParents

Relationships
 * Relationship object
 * createRelationship
 * getRelationships

Policies
 * Policy object
 * createPolicy
 * applyPolicy
 * removePolicy
 * getAppliedPolicies

Object Types
 * ObjectType methods

ACLs
 * ACL object
 * getACL
 * applyACL