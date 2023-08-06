#
# Copyright 2009 Optaros, Inc.
#
"""
Module containing the domain objects used to work with a CMIS provider.
"""
from cmislib.net import RESTService as Rest
from cmislib.exceptions import CmisException, RuntimeException, \
    ObjectNotFoundException, InvalidArgumentException, \
    PermissionDeniedException, NotSupportedException, \
    UpdateConflictException
from urllib import urlencode, quote_plus
from urllib2 import HTTPError
import re
import mimetypes

# would kind of like to not have any parsing logic in this module,
# but for now I'm going to put the serial/deserialization in methods
# of the CMIS object classes
from xml.dom import minidom

# Namespaces
ATOM_NS = 'http://www.w3.org/2005/Atom'
APP_NS = 'http://www.w3.org/2007/app'
CMISRA_NS = 'http://docs.oasis-open.org/ns/cmis/restatom/200908/'
CMIS_NS = 'http://docs.oasis-open.org/ns/cmis/core/200908/'

# Content types
ATOM_XML_TYPE = 'application/atom+xml'
ATOM_XML_ENTRY_TYPE = 'application/atom+xml;type=entry'
ATOM_XML_FEED_TYPE = 'application/atom+xml;type=feed'
CMIS_TREE_TYPE = 'application/cmistree+xml'
CMIS_QUERY_TYPE = 'application/cmisquery+xml'

# Standard rels
TYPE_DESCENDANTS_REL = 'http://docs.oasis-open.org/ns/cmis/link/200908/typedescendants'
FIRST_REL = 'first'
LAST_REL = 'last'
PREV_REL = 'prev'
NEXT_REL = 'next'
SELF_REL = 'self'

# Collection types
QUERY_COLL = 'query'
TYPES_COLL = 'types'
CHECKED_OUT_COLL = 'checkedout'
UNFILED_COLL = 'unfiled'
ROOT_COLL = 'root'


class CmisClient:

    """
    Handles all communication with the CMIS provider.
    """

    def __init__(self, repositoryUrl, username, password):

        """
        This is the entry point to the API. You need to know the
        :param repositoryUrl: The service URL of the CMIS provider
        :param username: Username
        :param password: Password

        >>> client = CmisClient('http://localhost:8080/alfresco/s/cmis', 'admin', 'admin')
        """

        self.repositoryUrl = repositoryUrl
        self.username = username
        self.password = password

    def getRepositories(self):

        """
        Returns a dict of high-level info about the repositories available at
        this service. The dict contains entries for 'repositoryId' and
        'repositoryName'.

        See CMIS specification document 2.2.2.1 getRepositories

        >>> client.getRepositories()
        [{'repositoryName': u'Main Repository', 'repositoryId': u'83beb297-a6fa-4ac5-844b-98c871c0eea9'}]
        """

        result = self.get(self.repositoryUrl)
        if (type(result) == HTTPError):
            raise RuntimeException()

        workspaceElements = result.getElementsByTagNameNS(APP_NS, 'workspace')
        # instantiate a Repository object using every workspace element
        # in the service URL then ask the repository object for its ID
        # and name, and return that back

        repositories = []
        for node in [e for e in workspaceElements if e.nodeType == e.ELEMENT_NODE]:
            repository = Repository(self, node)
            repositories.append({'repositoryId': repository.getRepositoryId(),
                                 'repositoryName': repository.getRepositoryInfo()['repositoryName']})
        return repositories

    def getRepository(self, repositoryId):

        """
        Returns the repository identified by the specified repositoryId.

        >>> repo = client.getRepository('83beb297-a6fa-4ac5-844b-98c871c0eea9')
        >>> repo.getRepositoryName()
        u'Main Repository'
        """

        doc = self.get(self.repositoryUrl)
        workspaceElements = doc.getElementsByTagNameNS(APP_NS, 'workspace')

        for workspaceElement in workspaceElements:
            idElement = workspaceElement.getElementsByTagNameNS(CMIS_NS, 'repositoryId')
            if idElement[0].childNodes[0].data == repositoryId:
                return Repository(self, workspaceElement)

        raise ObjectNotFoundException

    def getDefaultRepository(self):

        """
        There does not appear to be anything in the spec that identifies
        a repository as being the default, so we'll define it to be the
        first one in the list.

        >>> repo = client.getDefaultRepository()
        >>> repo.getRepositoryId()
        u'83beb297-a6fa-4ac5-844b-98c871c0eea9'
        """

        doc = self.get(self.repositoryUrl)
        workspaceElements = doc.getElementsByTagNameNS(APP_NS, 'workspace')
        # instantiate a Repository object with the first workspace
        # element we find
        repository = Repository(self, [e for e in workspaceElements if e.nodeType == e.ELEMENT_NODE][0])
        return repository

    def get(self, url, **kwargs):

        """
        Does a get against the CMIS service. More than likely, you will not
        need to call this method. Instead, let the other objects to it for you.

        For example, if you need to get a specific object by object id, try
        :class:`Repository.getObject`. If you have a path instead of an object
        id, use :class:`Repository.getObjectByPath`. Or, you could start with
        the root folder (:class:`Repository.getRootFolder`) and drill down from
        there.
        """

        result = Rest().get(url,
                            username=self.username,
                            password=self.password,
                            **kwargs)
        if type(result) == HTTPError:
            self._processCommonErrors(result)
            return result
        else:
            return minidom.parse(result)

    def delete(self, url):

        """
        Does a delete against the CMIS service. More than likely, you will not
        need to call this method. Instead, let the other objects to it for you.

        For example, to delete a folder you'd call :class:`Folder.delete` and
        to delete a document you'd call :class:`Document.delete`.
        """

        result = Rest().delete(url,
                               username=self.username,
                               password=self.password)
        if type(result) == HTTPError:
            self._processCommonErrors(result)
            return result
        else:
            pass

    def post(self, url, payload, contentType):

        """
        Does a post against the CMIS service. More than likely, you will not
        need to call this method. Instead, let the other objects to it for you.

        For example, to update the properties on an object, you'd call
        :class:`CmisObject.updateProperties`. Or, to check in a document that's
        been checked out, you'd call :class:`Document.checkin` on the PWC.
        """

        result = Rest().post(url,
                             payload,
                             contentType,
                             username=self.username,
                             password=self.password)
        if type(result) != HTTPError:
            return minidom.parse(result)
        elif result.code == 201:
            return minidom.parse(result)
        else:
            self._processCommonErrors(result)
            return result

    def put(self, url, payload, contentType):

        """
        Does a put against the CMIS service. More than likely, you will not
        need to call this method. Instead, let the other objects to it for you.

        For example, to update the properties on an object, you'd call
        :class:`CmisObject.updateProperties`. Or, to check in a document that's
        been checked out, you'd call :class:`Document.checkin` on the PWC.
        """

        result = Rest().put(url,
                            payload,
                            contentType,
                            username=self.username,
                            password=self.password)
        if type(result) == HTTPError:
            self._processCommonErrors(result)
            return result
        else:
            return minidom.parse(result)

    def _processCommonErrors(self, error):

        """
        Maps HTTPErrors that are common to all to exceptions. Only errors
        that are truly global, like 401 not authorized, should be handled
        here. Callers should handle the rest.

        See CMIS specification document 3.2.4.1 Common CMIS Exceptions
        """

        if error.status == 401:
            raise PermissionDeniedException(error.status)
        elif error.status == 400:
            raise InvalidArgumentException(error.status)
        elif error.status == 404:
            raise ObjectNotFoundException(error.status)
        elif error.status == 403:
            raise PermissionDeniedException(error.status)
        elif error.status == 405:
            raise NotSupportedException(error.status)
        elif error.status == 409:
            raise UpdateConflictException(error.status)
        elif error.status == 500:
            raise RuntimeException(error.status)


class Repository:

    """
    Represents a CMIS repository. Will lazily populate itself by
    calling the repository CMIS service URL.

    You must pass in an instance of a CmisClient when creating an
    instance of this class.

    See CMIS specification document 2.1.1 Repository
    """

    def __init__(self, cmisClient, xmlDoc=None):
        """ Constructor """
        self._cmisClient = cmisClient
        self.xmlDoc = xmlDoc
        self._repositoryId = None
        self._repositoryName = None
        self._repositoryInfo = {}
        self._capabilities = {}
        self._uriTemplates = {}

    def reload(self):
        """
        This method will re-fetch the repository's XML data from the CMIS
        repository.
        """
        self.xmlDoc = self._cmisClient.get(self._cmisClient.repositoryUrl)
        self._initData()

    def _initData(self):
        """
        This method clears out any local variables that would be out of sync
        when data is re-fetched from the server.
        """
        self._repositoryId = None
        self._repositoryName = None
        self._repositoryInfo = {}
        self._capabilities = {}
        self._uriTemplates = {}

    def getRepositoryId(self):

        """
        Returns this repository's unique identifier

        >>> repo = client.getDefaultRepository()
        >>> repo.getRepositoryId()
        u'83beb297-a6fa-4ac5-844b-98c871c0eea9'
        """

        if self._repositoryId == None:
            if self.xmlDoc == None:
                self.reload()
            self._repositoryId = self.xmlDoc.getElementsByTagNameNS(CMIS_NS, 'repositoryId')[0].firstChild.data
        return self._repositoryId

    def getRepositoryName(self):

        """
        Returns this repository's name

        >>> repo = client.getDefaultRepository()
        >>> repo.getRepositoryName()
        u'Main Repository'
        """

        if self._repositoryName == None:
            if self.xmlDoc == None:
                self.reload()
            self._repositoryName = self.xmlDoc.getElementsByTagNameNS(CMIS_NS, 'repositoryName')[0].firstChild.data
        return self._repositoryName

    def getRepositoryInfo(self):

        """
        Returns a dict of repository information.

        See CMIS specification document 2.2.2.2 getRepositoryInfo

        >>> repo = client.getDefaultRepository()>>> repo.getRepositoryName()
        u'Main Repository'
        >>> info = repo.getRepositoryInfo()
        >>> for k,v in info.items():
        ...     print "%s:%s" % (k,v)
        ...
        cmisSpecificationTitle:Version 1.0 Committee Draft 04
        cmisVersionSupported:1.0
        repositoryDescription:None
        productVersion:3.2.0 (r2 2440)
        rootFolderId:workspace://SpacesStore/aa1ecedf-9551-49c5-831a-0502bb43f348
        repositoryId:83beb297-a6fa-4ac5-844b-98c871c0eea9
        repositoryName:Main Repository
        vendorName:Alfresco
        productName:Alfresco Repository (Community)
        """

        if not self._repositoryInfo:
            if self.xmlDoc == None:
                self.reload()
            repoInfoElement = self.xmlDoc.getElementsByTagNameNS(CMISRA_NS, 'repositoryInfo')[0]
            for node in repoInfoElement.childNodes:
                if node.nodeType == node.ELEMENT_NODE and node.localName != 'capabilities':
                    try:
                        data = node.childNodes[0].data
                    except:
                        data = None
                    self._repositoryInfo[node.localName] = data
        return self._repositoryInfo

    def getCapabilities(self):

        """
        Returns a dict of repository capabilities.

        >>> caps = repo.getCapabilities()
        >>> for k,v in caps.items():
        ...     print "%s:%s" % (k,v)
        ...
        PWCUpdatable:True
        VersionSpecificFiling:False
        Join:None
        ContentStreamUpdatability:anytime
        AllVersionsSearchable:False
        Renditions:None
        Multifiling:True
        GetFolderTree:True
        GetDescendants:True
        ACL:None
        PWCSearchable:True
        Query:bothcombined
        Unfiling:False
        Changes:None
        """

        if not self._capabilities:
            if self.xmlDoc == None:
                self.reload()
            capabilitiesElement = self.xmlDoc.getElementsByTagNameNS(CMIS_NS, 'capabilities')[0]
            for node in [e for e in capabilitiesElement.childNodes if e.nodeType == e.ELEMENT_NODE]:
                key = node.localName.replace('capability', '')
                value = parseValue(node.childNodes[0].data)
                self._capabilities[key] = value
        return self._capabilities

    def getRootFolder(self):
        """
        Returns the root folder of the repository

        >>> root = repo.getRootFolder()
        >>> root.getObjectId()
        u'workspace://SpacesStore/aa1ecedf-9551-49c5-831a-0502bb43f348'
        """
        # get the root folder id
        rootFolderId = self.getRepositoryInfo()['rootFolderId']
        # instantiate a Folder object using the ID
        folder = Folder(self._cmisClient, self, rootFolderId)
        # return it
        return folder

    def getFolder(self, folderId):

        """
        Returns a :class:`Folder` object for a specified folderId

        >>> someFolder = repo.getFolder('workspace://SpacesStore/aa1ecedf-9551-49c5-831a-0502bb43f348')
        >>> someFolder.getObjectId()
        u'workspace://SpacesStore/aa1ecedf-9551-49c5-831a-0502bb43f348'
        """

        retObject = self.getObject(folderId)
        return Folder(self._cmisClient, self, xmlDoc=retObject.xmlDoc)

    def getTypeChildren(self,
                        typeId=None):

        """
        Returns a list of :class:`ObjectType` objects corresponding to the
        child types of the type specified by the typeId.

        If no typeId is provided, the result will be the same as calling
        `self.getTypeDefinitions`

        See CMIS specification document 2.2.2.3 getTypeChildren

        These optional arguments are current unsupported:
         - includePropertyDefinitions
         - maxItems
         - skipCount

        >>> baseTypes = repo.getTypeChildren()
        >>> for baseType in baseTypes:
        ...     print baseType.getTypeId()
        ...
        cmis:folder
        cmis:relationship
        cmis:document
        cmis:policy
        """

        # Unfortunately, the spec does not appear to present a way to
        # know how to get the children of a specific type without first
        # retrieving the type, then asking it for one of its navigational
        # links.

        # if a typeId is specified, get it, then get its "down" link
        if typeId:
            targetType = self.getTypeDefinition(typeId)
            childrenUrl = targetType.getLink('down', ATOM_XML_FEED_TYPE)
            typesXmlDoc = self._cmisClient.get(childrenUrl)
            entryElements = typesXmlDoc.getElementsByTagNameNS(ATOM_NS, 'entry')
            types = []
            for entryElement in entryElements:
                objectType = ObjectType(self._cmisClient,
                                        self,
                                        xmlDoc=entryElement)
                types.append(objectType)
        # otherwise, if a typeId is not specified, return
        # the list of base types
        else:
            types = self.getTypeDefinitions()
        return types

    def getTypeDescendants(self, typeId=None):

        """
        Returns a list of :class:`ObjectType` objects corresponding to the
        descendant types of the type specified by the typeId.

        If no typeId is provided, the repository's "typesdescendants" URL
        will be called to determine the list of descendant types.

        See CMIS specification document 2.2.2.4 getTypeDescendants

        These optional arguments are currently unsupported:
         - depth
         - includePropertyDefinitions

        >>> allTypes = repo.getTypeDescendants()
        >>> for aType in allTypes:
        ...     print aType.getTypeId()
        ...
        cmis:folder
        F:cm:systemfolder
        F:act:savedactionfolder
        F:app:configurations
        F:fm:forums
        F:wcm:avmfolder
        F:wcm:avmplainfolder
        F:wca:webfolder
        F:wcm:avmlayeredfolder
        F:st:site
        F:app:glossary
        F:fm:topic
        """

        # TODO: Need to handle depth and includePropertyDefinitions

        # Unfortunately, the spec does not appear to present a way to
        # know how to get the children of a specific type without first
        # retrieving the type, then asking it for one of its navigational
        # links.
        if typeId:
            targetType = self.getTypeDefinition(typeId)
            descendUrl = targetType.getLink('down', CMIS_TREE_TYPE)

        else:
            descendUrl = self.getLink(TYPE_DESCENDANTS_REL)

        if not descendUrl:
            raise NotSupportedException("Could not determine the type descendants URL")

        typesXmlDoc = self._cmisClient.get(descendUrl)
        entryElements = typesXmlDoc.getElementsByTagNameNS(ATOM_NS, 'entry')
        types = []
        for entryElement in entryElements:
            objectType = ObjectType(self._cmisClient,
                                    self,
                                    xmlDoc=entryElement)
            types.append(objectType)
        return types

    def getTypeDefinitions(self):

        """
        Returns a list of :class:`ObjectType` objects representing
        the base types in the repository.

        >>> baseTypes = repo.getTypeDefinitions()
        >>> for baseType in baseTypes:
        ...     print baseType.getTypeId()
        ...
        cmis:folder
        cmis:relationship
        cmis:document
        cmis:policy
        """

        typesUrl = self.getCollectionLink(TYPES_COLL)
        typesXmlDoc = self._cmisClient.get(typesUrl)
        entryElements = typesXmlDoc.getElementsByTagNameNS(ATOM_NS, 'entry')
        types = []
        for entryElement in entryElements:
            objectType = ObjectType(self._cmisClient,
                                    self,
                                    xmlDoc=entryElement)
            types.append(objectType)
        # return the result
        return types

    def getTypeDefinition(self, typeId):

        """
        Returns an :class:`ObjectType` object for the specified object type id.

        See CMIS specification document 2.2.2.5 getTypeDefinition

        >>> folderType = repo.getTypeDefinition('cmis:folder')
        """

        objectType = ObjectType(self._cmisClient, self, typeId)
        objectType.reload()
        return objectType

    def getLink(self, rel):
        """
        Returns the HREF attribute of an Atom link element for the
        specified rel.
        """
        if self.xmlDoc == None:
            self.reload()

        linkElements = self.xmlDoc.getElementsByTagNameNS(ATOM_NS, 'link')

        for linkElement in linkElements:

            if linkElement.attributes.has_key('rel'):
                relAttr = linkElement.attributes['rel'].value

                if relAttr == rel:
                    return linkElement.attributes['href'].value

    def getCheckedOutDocs(self):

        """
        Returns a ResultSet of :class:`CmisObject` objects that
        are currently checked out.

        See CMIS specification document 2.2.3.6 getCheckedOutDocs

        >>> rs = repo.getCheckedOutDocs()
        >>> len(rs.getResults())
        2
        >>> for doc in repo.getCheckedOutDocs().getResults():
        ...     doc.getTitle()
        ...
        u'sample-a (Working Copy).pdf'
        u'sample-b (Working Copy).pdf'

        None of these optional arguments are current supported:
         - folderId
         - maxItems
         - skipCount
         - orderBy
         - filter
         - includeRelationships
         - renditionFilter
         - includeAllowableActions
        """

        return self.getCollection(CHECKED_OUT_COLL)

    def getObject(self,
                  objectId):

        """
        Returns an object given the specified object ID.

        See CMIS specification document 2.2.4.7 getObject

        >>> doc = repo.getObject('workspace://SpacesStore/f0c8b90f-bec0-4405-8b9c-2ab570589808')
        >>> doc.getTitle()
        u'sample-b.pdf'

        The following optional arguments are not currently supported:
         - filter
         - includeRelationships
         - includePolicyIds
         - renditionFilter
         - includeACL
         - includeAllowableActions
        """

        return getSpecializedObject(CmisObject(self._cmisClient, self, objectId))

    def getObjectByPath(self, path):

        """
        Returns an object given the path to the object.

        See CMIS specification document 2.2.4.9 getObjectByPath

        >>> doc = repo.getObjectByPath('/jeff test/sample-b.pdf')
        >>> doc.getTitle()
        u'sample-b.pdf'

        The following optional arguments are not currently supported:
         - filter
         - includeAllowableActions
        """

        # get the uritemplate
        template = self.getUriTemplates()['objectbypath']['template']

        # fill in the template with the path provided
        params = {
              '{path}': quote_plus(path, '/'),
              '{filter}': '',
              '{includeAllowableActions}': 'false',
              '{includePolicyIds}': 'false',
              '{includeRelationships}': 'false',
              '{includeACL}': 'false',
              '{renditionFilter}': ''}
        byObjectPathUrl = multiple_replace(params, template)

        # do a GET against the URL
        result = self._cmisClient.get(byObjectPathUrl)
        if type(result) == HTTPError:
            raise CmisException(result.code)

        # instantiate CmisObject objects with the results and return the list
        entryElements = result.getElementsByTagNameNS(ATOM_NS, 'entry')
        assert(len(entryElements) == 1), "Expected entry element in result from calling %s" % byObjectPathUrl
        return getSpecializedObject(CmisObject(self._cmisClient, self, xmlDoc=entryElements[0]))

    def query(self, statement):

        """
        Returns a list of :class:`CmisObject` objects based on the CMIS
        Query Language passed in as the statement. The actual objects
        returned will be instances of the appropriate child class based
        on the object's base type ID.

        In order for the results to be properly instantiated as objects,
        make sure you include 'cmis:objectId' as one of the fields in
        your select statement, or just use "SELECT \*".

        If you want the search results to automatically be instantiated with
        the appropriate sub-class of :class:`CmisObject` you must either
        include cmis:baseTypeId as one of the fields in your select statement
        or just use "SELECT \*".

        See CMIS specification document 2.2.6.1 query

        >>> q = "select * from cmis:document where cmis:name like '%test%'"
        >>> resultSet = repo.query(q)
        >>> len(resultSet.getResults())
        1
        >>> resultSet.hasNext()
        False

        The following optional arguments are not currently supported:
         - searchAllVersions
         - includeRelationships
         - renditionFilter
         - includeAllowableActions
         - maxItems
         - skipCount
        """

        # TODO: Need to implement all optional args
        if self.xmlDoc == None:
            self.reload()

        # get the URL this repository uses to accept query POSTs
        queryUrl = self.getCollectionLink(QUERY_COLL)

        # build the CMIS query XML that we're going to POST
        xmlDoc = self._getQueryXmlDoc(statement)

        # do the POST
        #print 'posting:%s' % xmlDoc.toxml()
        result = self._cmisClient.post(queryUrl,
                                       xmlDoc.toxml(),
                                       CMIS_QUERY_TYPE)
        if type(result) == HTTPError:
            raise CmisException(result.code)

        # return the result set
        return ResultSet(self._cmisClient, self, result)

    def getContentChanges(self):

        """
        See CMIS specification document 2.2.6.2 getContentChanges

        The following optional arguments are not yet supported:
         - changeLogToken
         - includeProperties
         - includePolicyIDs
         - includeACL
         - maxItems
        """

        if self.getCapabilities()['Changes'] == None:
            raise NotSupportedException
        else:
            raise NotImplementedError

    def createDocument(self,
                       name,
                       properties={},
                       parentFolder=None,
                       contentFile=None):

        """
        Creates a new :class:`Document` object. If the repository
        supports unfiled objects, you do not have to pass in
        a parent :class:`Folder` otherwise it is required.

        To create a document with an associated contentFile, pass in a
        File object.

        See CMIS specification document 2.2.4.1 createDocument

        >>> f = open('sample-a.pdf', 'rb')
        >>> doc = folder.createDocument('sample-a.pdf', contentFile=f)
        <cmislib.model.Document object at 0x105be5e10>
        >>> f.close()
        >>> doc.getTitle()
        u'sample-a.pdf'

        The following optional arguments are not currently supported:
         - versioningState
         - policies
         - addACEs
         - removeACEs
        """

        # if you didn't pass in a parent folder
        if parentFolder == None:
            # if the repository doesn't require fileable objects to be filed
            if self.getCapabilities()['Unfiling']:
                # has not been implemented
                raise NotImplementedError
            else:
                # this repo requires fileable objects to be filed
                raise InvalidArgumentException

        return parentFolder.createDocument(name, properties, contentFile)

    def createDocumentFromSource(self,
                                 sourceId,
                                 properties={},
                                 parentFolder=None):
        """
        This is not yet implemented.

        See CMIS specification document 2.2.4.2 createDocumentFromSource

        The following optional arguments are not yet supported:
         - versioningState
         - policies
         - addACEs
         - removeACEs
        """
        # TODO: To be implemented
        raise NotImplementedError

    def createFolder(self,
                     parentFolder,
                     name,
                     properties={}):

        """
        Creates a new :class:`Folder` object in the specified parentFolder.

        See CMIS specification document 2.2.4.3 createFolder

        >>> root = repo.getRootFolder()
        >>> folder = repo.createFolder(root, 'someFolder2')
        >>> folder.getTitle()
        u'someFolder2'
        >>> folder.getObjectId()
        u'workspace://SpacesStore/2224a63c-350b-438c-be72-8f425e79ce1f'

        The following optional arguments are not yet supported:
         - policies
         - addACEs
         - removeACEs
        """

        return parentFolder.createFolder(name, properties)

    def createRelationship(self, properties):
        """
        This has not yet been implemented.

        See CMIS specification document 2.2.4.4 createRelationship

        The following optional arguments are not currently not supported:
         - policies
         - addACEs
         - removeACEs
        """
        # TODO: To be implemented
        raise NotImplementedError

    def createPolicy(self, properties):
        """
        This has not yet been implemented.

        See CMIS specification document 2.2.4.5 createPolicy

        The following optional arguments are not currently not supported:
         - folderId
         - policies
         - addACEs
         - removeACEs
        """
        # TODO: To be implemented
        raise NotImplementedError

    def getUriTemplates(self):

        """
        Returns a list of the URI templates the repository service knows about.

        >>> templates = repo.getUriTemplates()
        >>> templates['typebyid']['mediaType']
        u'application/atom+xml;type=entry'
        >>> templates['typebyid']['template']
        u'http://localhost:8080/alfresco/s/cmis/type/{id}'
        """

        if self._uriTemplates == {}:

            if self.xmlDoc == None:
                self.reload()

            uriTemplateElements = self.xmlDoc.getElementsByTagNameNS(CMISRA_NS, 'uritemplate')

            for uriTemplateElement in uriTemplateElements:
                template = None
                templType = None
                mediatype = None

                for node in [e for e in uriTemplateElement.childNodes if e.nodeType == e.ELEMENT_NODE]:
                    if node.localName == 'template':
                        template = node.childNodes[0].data
                    elif node.localName == 'type':
                        templType = node.childNodes[0].data
                    elif node.localName == 'mediatype':
                        mediatype = node.childNodes[0].data

                self._uriTemplates[templType] = UriTemplate(template,
                                                       templType,
                                                       mediatype)

        return self._uriTemplates

    def getCollection(self, collectionType):

        """
        Returns a list of objects returned for the specified collection.

        If the query collection is requested, an exception will be raised.
        That collection isn't meant to be retrieved.

        If the types collection is specified, the method returns the result of
        `getTypeDefinitions`.

        >>> from cmislib.model import TYPES_COLL
        >>> types = repo.getCollection(TYPES_COLL)
        >>> len(types)
        4
        >>> types[0].getTypeId()
        u'cmis:folder'

        Otherwise, the collection URL is invoked, and a :class:`ResultSet` is
        returned.

        >>> from cmislib.model import CHECKED_OUT_COLL
        >>> resultSet = repo.getCollection(CHECKED_OUT_COLL)
        >>> len(resultSet.getResults())
        1
        """

        if collectionType == QUERY_COLL:
            raise NotSupportedException
        elif collectionType == TYPES_COLL:
            return self.getTypeDefinitions()

        result = self._cmisClient.get(self.getCollectionLink(collectionType))
        if (type(result) == HTTPError):
            raise CmisException(result.code)

        # return the result set
        return ResultSet(self._cmisClient, self, result)

    def getCollectionLink(self, collectionType):

        """
        Returns the link HREF from the specified collectionType
        ('checkedout', for example).

        >>> from cmislib.model import CHECKED_OUT_COLL
        >>> repo.getCollectionLink(CHECKED_OUT_COLL)
        u'http://localhost:8080/alfresco/s/cmis/checkedout'

        """

        collectionElements = self.xmlDoc.getElementsByTagNameNS(APP_NS, 'collection')
        for collectionElement in collectionElements:
            link = collectionElement.attributes['href'].value
            for node in [e for e in collectionElement.childNodes if e.nodeType == e.ELEMENT_NODE]:
                if node.localName == 'collectionType':
                    if node.childNodes[0].data == collectionType:
                        return link

    def _getQueryXmlDoc(self, query):

        """
        Utility method that knows how to build CMIS query xml around the
        specified query statement.
        """

        # TODO: need to implement skipCount, maxitems, and other optional args
        cmisXmlDoc = minidom.Document()
        queryElement = cmisXmlDoc.createElementNS(CMIS_NS, "query")
        queryElement.setAttribute('xmlns', CMIS_NS)
        cmisXmlDoc.appendChild(queryElement)

        statementElement = cmisXmlDoc.createElementNS(CMIS_NS, "statement")
        cdataSection = cmisXmlDoc.createCDATASection(query)
        statementElement.appendChild(cdataSection)
        queryElement.appendChild(statementElement)

        return cmisXmlDoc


class ResultSet():

    """
    Represents a paged result set. In CMIS, this is most often an Atom feed.
    """

    def __init__(self, cmisClient, repository, xmlDoc):
        ''' Constructor '''
        self._cmisClient = cmisClient
        self._repository = repository
        self._xmlDoc = xmlDoc
        self._results = []

    def _getLink(self, rel):
        '''
        Returns the link found in the feed's XML for the specified rel.
        '''
        linkElements = self._xmlDoc.getElementsByTagNameNS(ATOM_NS, 'link')

        for linkElement in linkElements:

            if linkElement.attributes.has_key('rel') and \
               linkElement.attributes.has_key('type'):
                relAttr = linkElement.attributes['rel'].value
                typeAttr = linkElement.attributes['type'].value

                if relAttr == rel and typeAttr == ATOM_XML_FEED_TYPE:
                    return linkElement.attributes['href'].value

    def _getPageResults(self, rel):
        '''
        Given a specified rel, does a get using that link (if one exists)
        and then converts the resulting XML into a dictionary of
        :class:`CmisObject` objects or its appropriate sub-type.

        The results are kept around to facilitate repeated calls without moving
        the cursor.
        '''
        link = self._getLink(rel)
        if link:
            result = self._cmisClient.get(link)
            if (type(result) == HTTPError):
                raise CmisException(result.code)

            # return the result
            self._xmlDoc = result
            self._results = []
            return self.getResults()

    def reload(self):

        '''
        Re-invokes the self link for the current set of results.

        >>> resultSet = repo.getCollection(CHECKED_OUT_COLL)
        >>> resultSet.reload()

        '''

        self._getPageResults(SELF_REL)

    def getResults(self):

        '''
        Returns the results that were fetched and cached by the get*Page call.

        >>> resultSet = repo.getCheckedOutDocs()
        >>> resultSet.hasNext()
        False
        >>> for result in resultSet.getResults():
        ...     result
        ...
        <cmislib.model.Document object at 0x104851810>
        '''
        if self._results:
            return self._results

        if self._xmlDoc:
            entryElements = self._xmlDoc.getElementsByTagNameNS(ATOM_NS, 'entry')
            entries = []
            for entryElement in entryElements:
                cmisObject = getSpecializedObject(CmisObject(self._cmisClient,
                                                             self._repository,
                                                             xmlDoc=entryElement))
                entries.append(cmisObject)

            self._results = entries

        return self._results

    def getFirst(self):

        '''
        Returns the first page of results as a dictionary of
        :class:`CmisObject` objects or its appropriate sub-type. This only
        works when the server returns a "first" link. Not all of them do.

        >>> resultSet.hasFirst()
        True
        >>> results = resultSet.getFirst()
        >>> for result in results:
        ...     result
        ...
        <cmislib.model.Document object at 0x10480bc90>
        '''

        return self._getPageResults(FIRST_REL)

    def getPrev(self):

        '''
        Returns the prev page of results as a dictionary of
        :class:`CmisObject` objects or its appropriate sub-type. This only
        works when the server returns a "prev" link. Not all of them do.
        >>> resultSet.hasPrev()
        True
        >>> results = resultSet.getPrev()
        >>> for result in results:
        ...     result
        ...
        <cmislib.model.Document object at 0x10480bc90>
        '''

        return self._getPageResults(PREV_REL)

    def getNext(self):

        '''
        Returns the next page of results as a dictionary of
        :class:`CmisObject` objects or its appropriate sub-type.
        >>> resultSet.hasNext()
        True
        >>> results = resultSet.getNext()
        >>> for result in results:
        ...     result
        ...
        <cmislib.model.Document object at 0x10480bc90>
        '''

        return self._getPageResults(NEXT_REL)

    def getLast(self):

        '''
        Returns the last page of results as a dictionary of
        :class:`CmisObject` objects or its appropriate sub-type. This only
        works when the server is returning a "last" link. Not all of them do.

        >>> resultSet.hasLast()
        True
        >>> results = resultSet.getLast()
        >>> for result in results:
        ...     result
        ...
        <cmislib.model.Document object at 0x10480bc90>
        '''

        return self._getPageResults(LAST_REL)

    def hasNext(self):

        '''
        Returns True if this page contains a next link.

        >>> resultSet.hasNext()
        True
        '''

        if self._getLink(NEXT_REL):
            return True
        else:
            return False

    def hasPrev(self):

        '''
        Returns True if this page contains a prev link. Not all CMIS providers
        implement prev links consistently.

        >>> resultSet.hasPrev()
        True
        '''

        if self._getLink(PREV_REL):
            return True
        else:
            return False

    def hasFirst(self):

        '''
        Returns True if this page contains a first link. Not all CMIS providers
        implement first links consistently.

        >>> resultSet.hasFirst()
        True
        '''

        if self._getLink(FIRST_REL):
            return True
        else:
            return False

    def hasLast(self):

        '''
        Returns True if this page contains a last link. Not all CMIS providers
        implement last links consistently.

        >>> resultSet.hasLast()
        True
        '''

        if self._getLink(LAST_REL):
            return True
        else:
            return False


class CmisObject(object):

    """
    Common ancestor class for other CMIS domain objects such as
    :class:`Document` and :class:`Folder`.
    """

    def __init__(self, cmisClient, repository, objectId=None, xmlDoc=None):
        """ Constructor """
        self._cmisClient = cmisClient
        self._repository = repository
        self._objectId = objectId
        self._name = None
        self._properties = {}
        self._allowableActions = {}
        self.xmlDoc = xmlDoc
        # TODO: probably should go ahead and call reload just
        # in case someone gives us a bogus _objectId so we can
        # throw an exception

    def reload(self, **kwargs):

        """
        Fetches the latest representation of this object from the CMIS service.
        Some methods, like :class:`^Document.checkout` do this for you.
        """

        templates = self._repository.getUriTemplates()
        template = templates['objectbyid']['template']

        # Doing some refactoring here. Originally, we snagged the template
        # and then "filled in" the template based on the args passed in.
        # However, some servers don't provide a full template which meant
        # supported optional args wouldn't get passed in using the fill-the-
        # template approach. What's going on now is that the template gets
        # filled in where it can, but if additional, non-templated args are
        # passed in, those will get tacked on to the query string as
        # "additional" options.

        params = {
              '{id}': self.getObjectId(),
              '{filter}': '',
              '{includeAllowableActions}': 'false',
              '{includePolicyIds}': 'false',
              '{includeRelationships}': 'false',
              '{includeACL}': 'false',
              '{renditionFilter}': ''}

        options = {}
        addOptions = {} # args specified, but not in the template
        for k, v in kwargs.items():
            pKey = "{" + k + "}"
            if template.find(pKey) >= 0:
                options[pKey] = toCMISValue(v)
            else:
                addOptions[k] = toCMISValue(v)

        # merge the templated args with the default params
        params.update(options)

        # fill in the template
        byObjectIdUrl = multiple_replace(params, template)

        #self.xmlDoc = self._cmisClient.get(byObjectIdUrl)
        self.xmlDoc = self._cmisClient.get(byObjectIdUrl, **addOptions)
        self._initData()

    def _initData(self):

        """
        An internal method used to clear out any member variables that
        might be out of sync if we were to fetch new XML from the
        service.
        """

        self._properties = {}
        self._name = None
        self._allowableActions = {}

    def getObjectId(self):

        """
        Returns the object ID for this object.

        >>> doc = resultSet.getResults()[0]
        >>> doc.getObjectId()
        u'workspace://SpacesStore/dc26102b-e312-471b-b2af-91bfb0225339'
        """

        if self._objectId == None:
            if self.xmlDoc == None:
                self.reload()
            props = self.getProperties()
            self._objectId = props['cmis:objectId']
        return self._objectId

    def getObjectParents(self):
        """
        This has not yet been implemented.

        See CMIS specification document 2.2.3.5 getObjectParents

        The following optional arguments are not supported:
         - filter
         - includeRelationships
         - renditionFilter
         - includeAllowableActions
         - includeRelativePathSegment
        """

        # TODO To be implemented
        raise NotImplementedError

    def getAllowableActions(self):

        """
        Returns a dictionary of allowable actions, keyed off of the action name.

        >>> actions = doc.getAllowableActions()
        >>> for a in actions:
        ...     print "%s:%s" % (a,actions[a])
        ...
        canDeleteContentStream:True
        canSetContentStream:True
        canCreateRelationship:True
        canCheckIn:False
        canApplyACL:False
        canDeleteObject:True
        canGetAllVersions:True
        canGetObjectParents:True
        canGetProperties:True

        See CMIS specification document 2.2.4.6 getAllowableActions
        """

        if self._allowableActions == {}:
            self.reload(includeAllowableActions=True)
            allowElements = self.xmlDoc.getElementsByTagNameNS(CMIS_NS, 'allowableActions')
            assert len(allowElements) == 1, "Expected response to have exactly one allowableActions element"
            allowElement = allowElements[0]
            for node in [e for e in allowElement.childNodes if e.nodeType == e.ELEMENT_NODE]:
                actionName = node.localName
                actionValue = parseValue(node.childNodes[0].data)
                self._allowableActions[actionName] = actionValue

        return self._allowableActions

    def getTitle(self):

        """
        Returns the value of the object's cmis:title property.
        """

        if self.xmlDoc == None:
            self.reload()

        titleElement = self.xmlDoc.getElementsByTagNameNS(ATOM_NS, 'title')[0]

        if titleElement and titleElement.childNodes:
            return titleElement.childNodes[0].data

    def getProperties(self):

        """
        Returns a dict of the object's properties. If CMIS returns an
        empty element for a property, the property will be in the
        dict with a value of None.

        See CMIS specification document 2.2.4.8 getProperties

        >>> props = doc.getProperties()
        >>> for p in props:
        ...     print "%s: %s" % (p, props[p])
        ...
        cmis:contentStreamMimeType: text/html
        cmis:creationDate: 2009-12-15T09:45:35.369-06:00
        cmis:baseTypeId: cmis:document
        cmis:isLatestMajorVersion: false
        cmis:isImmutable: false
        cmis:isMajorVersion: false
        cmis:objectId: workspace://SpacesStore/dc26102b-e312-471b-b2af-91bfb0225339

        The optional filter argument is not yet implemented.
        """

        #TODO implement filter
        if self._properties == {}:
            if self.xmlDoc == None:
                self.reload()
            propertiesElement = self.xmlDoc.getElementsByTagNameNS(CMIS_NS, 'properties')[0]
            #cpattern = re.compile(r'^property([\w]*)')
            for node in [e for e in propertiesElement.childNodes if e.nodeType == e.ELEMENT_NODE]:
                #propertyId, propertyString, propertyDateTime
                #propertyType = cpattern.search(node.localName).groups()[0]
                propertyName = node.attributes['propertyDefinitionId'].value
                if node.childNodes and \
                   node.getElementsByTagNameNS(CMIS_NS, 'value')[0] and \
                   node.getElementsByTagNameNS(CMIS_NS, 'value')[0].childNodes:
                    propertyValue = node.getElementsByTagNameNS(CMIS_NS, 'value')[0].childNodes[0].data
                else:
                    propertyValue = None
                self._properties[propertyName] = propertyValue
        return self._properties

    def getName(self):

        """
        Returns the value of cmis:name from the getProperties() dictionary.
        We don't need a getter for every standard CMIS property, but name
        is a pretty common one so it seems to make sense.

        >>> doc.getName()
        u'system-overview.html'
        """

        if self._name == None:
            self._name = self.getProperties()['cmis:name']
        return self._name

    def updateProperties(self, properties):

        """
        Updates the properties of an object with the properties provided.
        Only provide the set of properties that need to be updated.

        See CMIS specification document 2.2.4.12 updateProperties

        >>> folder = repo.getObjectByPath('/someFolder2')
        >>> folder.getName()
        u'someFolder2'
        >>> props = {'cmis:name': 'someFolderFoo'}
        >>> folder.updateProperties(props)
        <cmislib.model.Folder object at 0x103ab1210>
        >>> folder.getName()
        u'someFolderFoo'

        The optional changeToken is not yet supported.
        """

        # TODO need to support the changeToken

        # get the self link
        selfUrl = self._getSelfLink()

        # build the entry based on the properties provided
        xmlEntryDoc = self._getEntryXmlDoc(properties)

        # do a PUT of the entry
        updatedXmlDoc = self._cmisClient.put(selfUrl,
                                             xmlEntryDoc.toxml(),
                                             ATOM_XML_TYPE)

        # reset the xmlDoc for this object with what we got back from
        # the PUT, then call initData we dont' want to call
        # self.reload because we've already got the parsed XML--
        # there's no need to fetch it again
        self.xmlDoc = updatedXmlDoc
        self._initData()
        return self

    def move(self, targetFolderId, sourceFolderId):

        """
        This is not yet implemented.

        See CMIS specification document 2.2.4.13 move
        """

        raise NotImplementedError

    def delete(self):

        """
        Deletes this :class:`CmisObject` from the repository. Note that in the
        case of a :class:`Folder` object, some repositories will refuse to
        delete it if it contains children and some will delete it without
        complaint. If what you really want to do is delete the folder and all
        of its descendants, use :meth:`~Folder.deleteTree` instead.

        See CMIS specification document 2.2.4.14 delete

        >>> folder.delete()

        The optional allVersions argument is not yet supported.
        """

        # TODO: Need to support allVersions

        url = self._getSelfLink()
        result = self._cmisClient.delete(url)

        if type(result) == HTTPError:
            raise CmisException(result.code)

    def applyPolicy(self, policyId):

        """
        This is not yet implemented.

        See CMIS specification document 2.2.9.1 applyPolicy
        """

        # depends on this object's canApplyPolicy allowable action
        if self.getAllowableActions()['canApplyPolicy']:
            raise NotImplementedError
        else:
            raise CmisException('This object has canApplyPolicy set to false')

    def removePolicy(self, policyId):

        """
        This is not yet implemented.

        See CMIS specification document 2.2.9.2 removePolicy
        """

        # depends on this object's canRemovePolicy allowable action
        if self.getAllowableActions()['canRemovePolicy']:
            raise NotImplementedError
        else:
            raise CmisException('This object has canRemovePolicy set to false')

    def getAppliedPolicies(self):

        """
        This is not yet implemented.

        See CMIS specification document 2.2.9.3 getAppliedPolicies
        """

        # depends on this object's canGetAppliedPolicies allowable action
        if self.getAllowableActions()['canGetAppliedPolicies']:
            raise NotImplementedError
        else:
            raise CmisException('This object has canGetAppliedPolicies set to false')

    def getACL(self):

        """
        Repository.getCapabilities['ACL'] must return manage or discover.

        See CMIS specification document 2.2.10.1 getACL

        The optional onlyBasicPermissions argument is currently not supported.
        """

        if self._repository.getCapabilities()['ACL']:
            # if the ACL capability is discover or manage, this must be
            # supported
            raise NotImplementedError
        else:
            raise NotSupportedException

    def applyACL(self):

        """
        Repository.getCapabilities['ACL'] must return manage.

        See CMIS specification document 2.2.10.2 applyACL

        The following optional arguments are currently not supported:
         - addACEs
         - removeACEs
         - ACLPropagation
        """

        if self._repository.getCapabilities()['ACL'] == 'manage':
            # if the ACL capability is manage, this must be
            # supported
            # but it also depends on the canApplyACL allowable action
            # for this object
            raise NotImplementedError
        else:
            raise NotSupportedException

    def _getSelfLink(self):

        """
        Returns the URL used to retrieve this object.
        """

        return self._getLink('self')

    def _getLink(self, rel, type=None):

        """
        Returns the HREF attribute of an Atom link element for the
        specified rel.
        """

        if self.xmlDoc == None:
            self.reload()
        linkElements = self.xmlDoc.getElementsByTagNameNS(ATOM_NS, 'link')

        for linkElement in linkElements:

            if type:
                if linkElement.attributes.has_key('rel'):
                    relAttr = linkElement.attributes['rel'].value

                    if type and linkElement.attributes.has_key('type'):
                        typeAttr = linkElement.attributes['type'].value

                        if relAttr == rel and typeAttr == type:
                            return linkElement.attributes['href'].value
            else:
                if linkElement.attributes.has_key('rel'):
                    relAttr = linkElement.attributes['rel'].value

                    if relAttr == rel:
                        return linkElement.attributes['href'].value

    def _getEmptyXmlDoc(self):

        """
        Internal helper method that knows how to build an empty Atom entry.
        """

        entryXmlDoc = minidom.Document()
        entryElement = entryXmlDoc.createElementNS(ATOM_NS, "entry")
        entryElement.setAttribute('xmlns', ATOM_NS)
        entryXmlDoc.appendChild(entryElement)
        return entryXmlDoc

    def _getEntryXmlDoc(self, properties=None, contentFile=None):

        """
        Internal helper method that knows how to build an Atom entry based
        on the properties and, optionally, the contentFile provided.
        """

        entryXmlDoc = minidom.Document()
        entryElement = entryXmlDoc.createElementNS(ATOM_NS, "entry")
        entryElement.setAttribute('xmlns', ATOM_NS)
        entryElement.setAttribute('xmlns:app', APP_NS)
        entryElement.setAttribute('xmlns:cmisra', CMISRA_NS)
        entryXmlDoc.appendChild(entryElement)

        # if there is a File, encode it and add it to the XML
        if contentFile:
            # need to determine the mime type
            mimetype, encoding = mimetypes.guess_type(contentFile.name)
            if not mimetype:
                mimetype = 'application/binary'

            # This used to be ATOM_NS content but there is some debate among
            # vendors whether the ATOM_NS content must always be base64
            # encoded. The spec does mandate that CMISRA_NS content be encoded
            # and that element takes precedence over ATOM_NS content if it is
            # present, so it seems reasonable to use CMIS_RA content for now
            # and encode everything.

            # I am stripping the line breaks here because FileNet will create
            # a 0-byte content stream if the base64 characters include breaks
            # even though MIME-compliant decoders are supposed to ignore breaks

            fileData = contentFile.read().encode("base64").replace('\n', '')
            contentElement = entryXmlDoc.createElementNS(CMISRA_NS, 'cmisra:content')
            mediaElement = entryXmlDoc.createElementNS(CMISRA_NS, 'cmisra:mediatype')
            mediaElementText = entryXmlDoc.createTextNode(mimetype)
            mediaElement.appendChild(mediaElementText)
            base64Element = entryXmlDoc.createElementNS(CMISRA_NS, 'cmisra:base64')
            base64ElementText = entryXmlDoc.createTextNode(fileData)
            base64Element.appendChild(base64ElementText)
            contentElement.appendChild(mediaElement)
            contentElement.appendChild(base64Element)

            entryElement.appendChild(contentElement)

        objectElement = entryXmlDoc.createElementNS(CMISRA_NS, 'cmisra:object')
        objectElement.setAttribute('xmlns:cmis', CMIS_NS)
        entryElement.appendChild(objectElement)

        if properties:
            # a name is required for most things, but not for a checkout
            if properties.has_key('cmis:name'):
                titleElement = entryXmlDoc.createElementNS(ATOM_NS, "title")
                titleText = entryXmlDoc.createTextNode(properties['cmis:name'])
                titleElement.appendChild(titleText)
                entryElement.appendChild(titleElement)

            propsElement = entryXmlDoc.createElementNS(CMIS_NS, 'cmis:properties')
            objectElement.appendChild(propsElement)

            for propName, propValue in properties.items():
                """
                the name of the element here is significant. maybe rather
                than a simple string, I should be passing around property
                objects because I kind of need to know the type.
                It may be possible to guess a date time from a string,
                but an ID will be harder.

                for now I'll just guess the type based on the property name.
                """
                # TODO: Need to support property types other than String, Id,
                # and DateTime see 2.1.2.1 Property
                # TODO: Need a less hackish way to determine property type
                if propName.endswith('String'):
                    propElementName = 'cmis:propertyString'
                elif propName.endswith('Id'):
                    propElementName = 'cmis:propertyId'
                elif propName.endswith('Date') or propName.endswith('DateTime'):
                    propElementName = 'cmis:propertyDateTime'
                else:
                    propElementName = 'cmis:propertyString'

                propElement = entryXmlDoc.createElementNS(CMIS_NS, propElementName)
                propElement.setAttribute('propertyDefinitionId', propName)
                valElement = entryXmlDoc.createElementNS(CMIS_NS, 'cmis:value')
                val = entryXmlDoc.createTextNode(propValue)
                valElement.appendChild(val)
                propElement.appendChild(valElement)
                propsElement.appendChild(propElement)

        return entryXmlDoc


class Document(CmisObject):

    """
    An object typically associated with file content.
    """

    def checkout(self):

        """
        Performs a checkout on the :class:`Document` and returns the
        Private Working Copy (PWC), which is also an instance of
        :class:`Document`

        See CMIS specification document 2.2.7.1 checkout

        >>> doc.getObjectId()
        u'workspace://SpacesStore/f0c8b90f-bec0-4405-8b9c-2ab570589808;1.0'
        >>> doc.isCheckedOut()
        False
        >>> pwc = doc.checkout()
        >>> doc.isCheckedOut()
        True
        """

        # TODO: should check allowable actions to make sure a checkout is okay

        # get the checkedout collection URL
        checkoutUrl = self._repository.getCollectionLink(CHECKED_OUT_COLL)

        # get this document's object ID
        # build entry XML with it
        properties = {'cmis:objectId': self.getObjectId()}
        entryXmlDoc = self._getEntryXmlDoc(properties)

        # post it to to the checkedout collection URL
        result = self._cmisClient.post(checkoutUrl,
                                       entryXmlDoc.toxml(),
                                       ATOM_XML_ENTRY_TYPE)

        if type(result) == HTTPError:
            raise CmisException(result.code)

        # now that the doc is checked out, we need to refresh the XML
        # to pick up the prop updates related to a checkout
        self.reload()

        return Document(self._cmisClient, self._repository, xmlDoc=result)

    def cancelCheckout(self):
        """
        Cancels the checkout of this object by retrieving the Private Working
        Copy (PWC) and then deleting it. After the PWC is deleted, this object
        will be reloaded to update properties related to a checkout.

        See CMIS specification document 2.2.7.2 cancelCheckOut

        >>> doc.isCheckedOut()
        True
        >>> doc.cancelCheckout()
        >>> doc.isCheckedOut()
        False
        """

        pwcDoc = self.getPrivateWorkingCopy()
        if pwcDoc:
            pwcDoc.delete()
            self.reload()

    def getPrivateWorkingCopy(self):

        """
        Retrieves the object using the object ID in the property:
        cmis:versionSeriesCheckedOutId then uses getObject to instantiate
        the object.

        >>> doc.isCheckedOut()
        False
        >>> doc.checkout()
        <cmislib.model.Document object at 0x103a25ad0>
        >>> pwc = doc.getPrivateWorkingCopy()
        >>> pwc.getTitle()
        u'sample-b (Working Copy).pdf'
        """

        # reloading the document just to make sure we've got the latest
        # and greatest PWC ID
        self.reload()
        pwcDocId = self.getProperties()['cmis:versionSeriesCheckedOutId']
        if pwcDocId:
            return self._repository.getObject(pwcDocId)

    def isCheckedOut(self):

        """
        Returns true if the document is checked out.

        >>> doc.isCheckedOut()
        True
        >>> doc.cancelCheckout()
        >>> doc.isCheckedOut()
        False
        """

        # reloading the document just to make sure we've got the latest
        # and greatest checked out prop
        self.reload()
        return parseValue(self.getProperties()['cmis:isVersionSeriesCheckedOut'])

    def getCheckedOutBy(self):

        """
        Returns the ID who currently has the document checked out.
        >>> pwc = doc.checkout()
        >>> pwc.getCheckedOutBy()
        u'admin'
        """

        # reloading the document just to make sure we've got the latest
        # and greatest checked out prop
        self.reload()
        return self.getProperties()['cmis:versionSeriesCheckedOutBy']

    def checkin(self, checkinComment=None):

        """
        Checks in this :class:`Document` which must be a private
        working copy (PWC).

        See CMIS specification document 2.2.7.3 checkIn

        >>> doc.isCheckedOut()
        False
        >>> pwc = doc.checkout()
        >>> doc.isCheckedOut()
        True
        >>> pwc.checkin()
        <cmislib.model.Document object at 0x103a8ae90>
        >>> doc.isCheckedOut()
        False

        The following optional arguments are not currently supported:
         - major
         - properties
         - contentStream
         - policies
         - addACEs
         - removeACEs
        """

        # TODO: need to handle major flag, properties, contentStream,
        # and the rest of the optional args
        # Get the self link

        # Need to fix this when we start adding other optional args
        # to the URL
        url = self._getSelfLink() + '?checkin=true'
        if checkinComment:
            url += '&' + urlencode(dict(checkinComment=checkinComment))

        # Build an empty ATOM entry
        entryXmlDoc = self._getEmptyXmlDoc()

        # Do a PUT of the empty ATOM to the self link
        result = self._cmisClient.put(url, entryXmlDoc.toxml(), ATOM_XML_TYPE)

        if type(result) == HTTPError:
            raise CmisException(result.code)

        return Document(self._cmisClient, self._repository, xmlDoc=result)

    def getLatestVersion(self):

        """
        This is not yet implemented.

        See CMIS specification document 2.2.7.4 getObjectOfLatestVersion

        The following optional arguments are not yet supported:
         - major
         - filter
         - includeRelationships
         - includePolicyIds
         - renditionFilter
         - includeACL
         - includeAllowableActions
        """

        # TODO: To be implemented
        raise NotImplementedError

    def getPropertiesOfLatestVersion(self):

        """
        This is not yet implemented.

        See CMIS specification document 2.2.7.4 getPropertiesOfLatestVersion

        The optional major and filter arguments are not yet supported.
        """

        # TODO: To be implemented
        raise NotImplementedError

    def getAllVersions(self):

        """
        This is not yet implemented.

        See CMIS specification document 2.2.7.5 getAllVersions

        The optional filter and includeAllowableActions arguments are not
        yet supported.
        """

        # TODO: To be implemented
        raise NotImplementedError

    def getRelationships(self):

        """
        This is not yet implemented.

        See CMIS specification document 2.2.8.1 getObjectRelationships

        The following optional arguments are not yet supported:
         - includeSubRelationshipTypes
         - relationshipDirection
         - typeId
         - maxItems
         - skipCount
         - filter
         - includeAllowableActions
        """

        # TODO: To be implemented
        raise NotImplementedError

    def getContentStream(self):

        """
        Returns the CMIS service response from invoking the 'enclosure' link.

        See CMIS specification document 2.2.4.10 getContentStream

        >>> doc.getName()
        u'sample-b.pdf'
        >>> o = open('tmp.pdf', 'wb')
        >>> result = doc.getContentStream()
        >>> o.write(result.read())
        >>> result.close()
        >>> o.close()
        >>> import os.path
        >>> os.path.getsize('tmp.pdf')
        117248

        The optional streamId argument is not yet supported.
        """

        # TODO: Need to implement the streamId

        url = self._getLink('enclosure')
        # the cmis client class parses non-error responses
        result = Rest().get(url,
                            username=self._cmisClient.username,
                            password=self._cmisClient.password)
        if result.code != 200:
            raise CmisException(result.code)
        return result

    def setContentStream(self, contentFile):

        """
        See CMIS specification document 2.2.4.16 setContentStream

        The following optional arguments are not yet supported:
         - overwriteFlag=None,
         - changeToken=None
        """

        # TODO: THIS IS CURRENTLY VERY BROKEN...don't think I understand what the intent of this method is

        # get this object's enclosure link
        postUrl = self._getLink('enclosure')

        # build the Atom entry
        xmlDoc = self._getEntryXmlDoc(contentFile=contentFile)

        # post the Atom entry
        result = self._cmisClient.put(postUrl, xmlDoc.toxml(), ATOM_XML_TYPE)
        if type(result) == HTTPError:
            raise CmisException(result.code)

        # what comes back is the XML for the updated document,
        # which is not required by the spec to be the same document
        # we just updated, so use it to instantiate a new document
        # then return it
        return Document(self._cmisClient, self._repository, xmlDoc=result)

    def deleteContentStream(self, changeToken=None):

        """
        See CMIS specification document 2.2.4.17 deleteContentStream
        """

        # TODO: To be implemented
        raise NotImplementedError

    def getRenditions(self):

        """
        This is not yet supported.

        See CMIS specification document 2.2.4.11 getRenditions

        The following optional arguments are not currently supported:
         - renditionFilter
         - maxItems
         - skipCount
        """

        # if Renditions capability is None, return notsupported
        if self._repository.getCapabilities()['Renditions']:
            raise NotImplementedError
        else:
            raise NotSupportedException


class Folder(CmisObject):

    """
    A container object that can hold other :class:`CmisObject` objects
    """

    def createFolder(self, name, properties={}):

        """
        Creates a new :class:`Folder` using the properties provided.
        Right now I expect a property called 'cmis:name' but I don't
        complain if it isn't there (although the CMIS provider will)

        See CMIS specification document 2.2.4.3 createFolder

        >>> subFolder = folder.createFolder('someSubfolder')
        >>> subFolder.getName()
        u'someSubfolder'

        The following optional arguments are not yet supported:
         - policies
         - addACEs
         - removeACEs
        """

        # get the folder represented by folderId.
        # we'll use his 'children' link post the new child
        postUrl = self._getChildrenLink()

        # make sure the name property gets set
        properties['cmis:name'] = name

        # hardcoding to cmis:folder if it wasn't passed in via props
        if not properties.has_key('cmis:objectTypeId'):
            properties['cmis:objectTypeId'] = 'cmis:folder'

        # build the Atom entry
        entryXml = self._getEntryXmlDoc(properties)

        # post the Atom entry
        result = self._cmisClient.post(postUrl,
                                       entryXml.toxml(),
                                       ATOM_XML_TYPE)
        if type(result) == HTTPError:
            raise CmisException(result.code)

        # what comes back is the XML for the new folder,
        # so use it to instantiate a new folder then return it
        return Folder(self._cmisClient, self._repository, xmlDoc=result)

    def createDocument(self, name, properties={}, contentFile=None):

        """
        Creates a new Document object in the repository using
        the properties provided.

        Right now this is basically the same as createFolder,
        but this deals with contentStreams. The common logic should
        probably be moved to CmisObject.createObject.

        >>> f = open('250px-Cmis_logo.png', 'rb')
        >>> subFolder.createDocument('logo.png', contentFile=f)
        <cmislib.model.Document object at 0x10410fa10>
        >>> f.close()

        If you wanted to set one or more properties when creating the doc, pass
        in a dict, like this:

        >>> props = {'cmis:someProp':'someVal'}
        >>> f = open('250px-Cmis_logo.png', 'rb')
        >>> subFolder.createDocument('logo.png', props, contentFile=f)
        <cmislib.model.Document object at 0x10410fa10>
        >>> f.close()

        The following optional arguments are not yet supported:
         - versioningState
         - policies
         - addACEs
         - removeACEs
        """

        # get the folder represented by folderId.
        # we'll use his 'children' link post the new child
        postUrl = self._getChildrenLink()

        # make sure a name is set
        properties['cmis:name'] = name

        # hardcoding to cmis:document if it wasn't
        # passed in via props
        if not properties.has_key('cmis:objectTypeId'):
            properties['cmis:objectTypeId'] = 'cmis:document'

        # build the Atom entry
        xmlDoc = self._getEntryXmlDoc(properties, contentFile)

        # post the Atom entry
        result = self._cmisClient.post(postUrl, xmlDoc.toxml(), ATOM_XML_TYPE)
        if type(result) == HTTPError:
            raise CmisException(result.code)

        # what comes back is the XML for the new document,
        # so use it to instantiate a new document
        # then return it
        return Document(self._cmisClient, self._repository, xmlDoc=result)

    def getChildren(self):

        """
        Returns a paged :class:`ResultSet`. The result set contains a list of
        :class:`CmisObject` objects for each child of the Folder. The actual
        type of the object returned depends on the object's CMIS base type id.
        For example, the method might return a list that contains both
        :class:`Document` objects and :class:`Folder` objects.

        See CMIS specification document 2.2.3.1 getChildren

        >>> childrenRS = subFolder.getChildren()
        >>> children = childrenRS.getResults()

        The following optional arguments are not yet supported:
         - maxItems
         - skipCount
         - orderBy
         - filter
         - includeRelationships
         - renditionFilter
         - includeAllowableActions
         - includePathSegment
        """

        # get the appropriate 'down' link
        childrenUrl = self._getChildrenLink()
        # invoke the URL
        result = self._cmisClient.get(childrenUrl)

        if type(result) == HTTPError:
            raise CmisException(result.code)

        # return the result set
        return ResultSet(self._cmisClient, self._repository, result)

    def _getChildrenLink(self):

        """
        Gets the Atom link that knows how to return this object's children.
        """

        if self.xmlDoc == None:
            self.reload()

        linkElements = self.xmlDoc.getElementsByTagNameNS(ATOM_NS, 'link')

        for linkElement in linkElements:

            if linkElement.attributes.has_key('rel') and linkElement.attributes.has_key('type'):
                relAttr = linkElement.attributes['rel'].value
                typeAttr = linkElement.attributes['type'].value

                if relAttr == 'down' and typeAttr == ATOM_XML_FEED_TYPE:
                    return linkElement.attributes['href'].value

    def getDescendantsLink(self):

        """
        Returns the 'down' link of type `CMIS_TREE_TYPE`

        >>> folder.getDescendantsLink()
        u'http://localhost:8080/alfresco/s/cmis/s/workspace:SpacesStore/i/86f6bf54-f0e8-4a72-8cb1-213599ba086c/descendants'
        """

        if self.xmlDoc == None:
            self.reload()

        linkElements = self.xmlDoc.getElementsByTagNameNS(ATOM_NS, 'link')

        url = ''
        for linkElement in linkElements:

            if linkElement.attributes.has_key('rel') and linkElement.attributes.has_key('type'):
                relAttr = linkElement.attributes['rel'].value
                typeAttr = linkElement.attributes['type'].value

                if relAttr == 'down' and typeAttr == CMIS_TREE_TYPE:
                    url = linkElement.attributes['href'].value
                    break

        assert len(url) > 0, "Could not find the descendants url"

        # some servers return a depth arg as part of this URL
        # so strip it off
        if url.find("?") >= 0:
            url = url[:url.find("?")]

        return url

    def getDescendants(self, **kwargs):

        """
        Gets the descendants of this folder. The descendants are returned as
        a paged :class:`ResultSet` object. The result set contains a list of
        :class:`CmisObject` objects where the actual type of each object
        returned will vary depending on the object's base type id. For example,
        the method might return a list that contains both :class:`Document`
        objects and :class:`Folder` objects.

        See CMIS specification document 2.2.3.2 getDescendants

        The following optional argument is currently supported:
         - depth. Use depth=-1 for all descendants, which is the default if no
           depth is specified.

        >>> resultSet = folder.getDescendants()
        >>> len(resultSet.getResults())
        105
        >>> resultSet = folder.getDescendants(depth=1)
        >>> len(resultSet.getResults())
        103

        The following optional arguments *may* also work but haven't been
        tested:
         - filter
         - includeRelationships
         - renditionFilter
         - includeAllowableActions
         - includePathSegment

        """

        # default the depth to -1, which is all descendants
        if "depth" not in kwargs:
            kwargs['depth'] = -1

        # get the appropriate 'down' link
        descendantsUrl = self.getDescendantsLink()

        # invoke the URL
        result = self._cmisClient.get(descendantsUrl, **kwargs)

        if type(result) == HTTPError:
            raise CmisException(result.code)

        # return the result set
        return ResultSet(self._cmisClient, self._repository, result)

    def getTree(self):

        """
        This is not yet implemented.

        See CMIS specification document 2.2.3.3 getFolderTree

        The following optional arguments are currently unsupported:
         - depth
         - filter
         - includeRelationships
         - renditionFilter
         - includeAllowableActions
         - includePathSegment
        """

        # TODO: Need to implement
        raise NotImplementedError

    def getParent(self):

        """
        This is not yet implemented.

        See CMIS specification document 2.2.3.4 getFolderParent

        The optional filter argument is not yet supported.
        """
        # TODO: Need to implement
        # get this object's 'up' link, then invoke the URL, and return the resulting Folder object
        # note that the folder will always have an 'up' link except for the root folder
        raise NotImplementedError

    def deleteTree(self):

        """
        Deletes the folder and all of its descendant objects.

        See CMIS specification document 2.2.4.15 deleteTree

        >>> resultSet = subFolder.getDescendants()
        >>> len(resultSet.getResults())
        2
        >>> subFolder.deleteTree()

        The following optional arguments are not yet supported:
         - allVersions
         - unfileObjects
         - continueOnFailure
        """

        # TODO: Need to implement optional arguments

        # Get the descendants link and do a DELETE against it
        url = self._getLink('down', CMIS_TREE_TYPE)
        result = self._cmisClient.delete(url)

        if type(result) == HTTPError:
            raise CmisException(result.code)

    def addObject(self, cmisObject):

        """
        This is not yet implemented.

        See CMIS specification document 2.2.5.1 addObjectToFolder

        The optional allVersions argument is not yet supported.
        """

        # TODO: To be implemented.
        raise NotImplementedError

    def removeObject(self, cmisObject):

        """
        This is not yet implemented.

        See CMIS specification document 2.2.5.2 removeObjectFromFolder
        """

        # TODO: To be implemented
        raise NotImplementedError


class Relationship(CmisObject):

    """
    Defines a relationship object between two :class:`CmisObjects` objects
    """

    pass


class Policy(CmisObject):

    """
    An arbirary object that can 'applied' to objects that the
    repository identifies as being 'controllable'.
    """

    pass


class ObjectType:

    """
    Represents the CMIS object type such as 'cmis:document' or 'cmis:folder'.
    Contains metadata about the type.
    """

    def __init__(self, cmisClient, repository, typeId=None, xmlDoc=None):
        """ Constructor """
        self._cmisClient = cmisClient
        self._repository = repository
        self.typeId = typeId
        self.xmlDoc = xmlDoc

    def getTypeId(self):

        """
        Returns the type ID for this object.

        >>> docType = repo.getTypeDefinition('cmis:document')
        >>> docType.getTypeId()
        'cmis:document'
        """

        if self.typeId == None:
            if self.xmlDoc == None:
                self.reload()
            typeElement = self.xmlDoc.getElementsByTagNameNS(CMISRA_NS, 'type')[0]
            idElement = typeElement.getElementsByTagNameNS(CMIS_NS, 'id')[0]
            self.typeId = idElement.childNodes[0].data

        return self.typeId

    def getLink(self, rel, linkType):

        """
        Gets the HREF for the link element with the specified rel and linkType.

        >>> from cmislib.model import ATOM_XML_FEED_TYPE
        >>> docType.getLink('down', ATOM_XML_FEED_TYPE)
        u'http://localhost:8080/alfresco/s/cmis/type/cmis:document/children'
        """

        linkElements = self.xmlDoc.getElementsByTagNameNS(ATOM_NS, 'link')

        for linkElement in linkElements:

            if linkElement.attributes.has_key('rel') and linkElement.attributes.has_key('type'):
                relAttr = linkElement.attributes['rel'].value
                typeAttr = linkElement.attributes['type'].value

                if relAttr == rel and typeAttr == linkType:
                    return linkElement.attributes['href'].value

    def reload(self):
        """
        This method will reload the object's data from the CMIS service.
        """
        templates = self._repository.getUriTemplates()
        template = templates['typebyid']['template']
        params = {'{id}': self.typeId}
        byTypeIdUrl = multiple_replace(params, template)
        self.xmlDoc = self._cmisClient.get(byTypeIdUrl)


class UriTemplate(dict):

    """
    Simple dictionary to represent the data stored in
    a URI template entry.
    """

    def __init__(self, template, templateType, mediaType):
        """ Constructor """
        dict.__init__(self)
        self['template'] = template
        self['type'] = templateType
        self['mediaType'] = mediaType


def parseValue(value):

    """
    Utility function to parse booleans and none from strings
    """

    if value == 'false':
        return False
    elif value == 'true':
        return True
    elif value == 'none':
        return None
    else:
        return value


def toCMISValue(value):

    """
    Utility function to convert Python values to CMIS string values
    """

    if value == False:
        return 'false'
    elif value == True:
        return 'true'
    elif value == None:
        return 'none'
    else:
        return value


def multiple_replace(aDict, text):

    """
    Replace in 'text' all occurences of any key in the given
    dictionary by its corresponding value.  Returns the new string.

    See http://code.activestate.com/recipes/81330/
    """

    # Create a regular expression  from the dictionary keys
    regex = re.compile("(%s)" % "|".join(map(re.escape, aDict.keys())))

    # For each match, look-up corresponding value in dictionary
    return regex.sub(lambda mo: aDict[mo.string[mo.start():mo.end()]], text)


def getSpecializedObject(object):

    """
    Returns an instance of the appropriate :class:`CmisObject` class or one
    of its child types depending on the specified baseType.
    """

    if 'cmis:baseTypeId' in object.getProperties():
        baseType = object.getProperties()['cmis:baseTypeId']
        if baseType == 'cmis:folder':
            return Folder(object._cmisClient, object._repository, object.getObjectId(), object.xmlDoc)
        if baseType == 'cmis:document':
            return Document(object._cmisClient, object._repository, object.getObjectId(), object.xmlDoc)
        if baseType == 'cmis:relationship':
            return Relationship(object._cmisClient, object._repository, object.getObjectId(), object.xmlDoc)
        if baseType == 'cmis:policy':
            return Policy(object._cmisClient, object._repository, object.getObjectId(), object.xmlDoc)

    # if the base type ID wasn't found in the props (this can happen when
    # someone runs a query that doesn't select * or doesn't individually
    # specify baseTypeId) or if the type isn't one of the known base
    # types, give the object back
    return object
