#
# Copyright 2009 Optaros, Inc.
#
'''
Unit tests for cmislib
'''
import unittest
from cmislib.model import CmisClient
from cmislib.exceptions import \
                          ObjectNotFoundException, \
                          PermissionDeniedException, \
                          CmisException
import os
from time import sleep, time

#TODO: Move these out into a config file or something
REPOSITORY_URL = 'http://cmis.alfresco.com/s/cmis'
#REPOSITORY_URL = 'http://localhost:8080/alfresco/s/cmis'
#REPOSITORY_URL = 'http://cmis.demo.nuxeo.org/nuxeo/site/cmis/repository'
USERNAME = 'admin'
PASSWORD = 'admin'
#USERNAME = 'Administrator'
#PASSWORD = 'Administrator'


class CmisTestBase(unittest.TestCase):

    """ Common ancestor class for most cmislib unit test classes. """

    def setUp(self):
        """ Create a root test folder for the test. """
        self._cmisClient = CmisClient(REPOSITORY_URL, USERNAME, PASSWORD)
        self._repo = self._cmisClient.getDefaultRepository()
        self._rootFolder = self._repo.getRootFolder()
        self._folderName = " ".join(['cmislib', self.__class__.__name__, str(time())])
        self._testFolder = self._rootFolder.createFolder(self._folderName)

    def tearDown(self):
        """ Clean up after the test. """
        self._testFolder.deleteTree()


class CmisClientTest(unittest.TestCase):

    """ Tests for the :class:`CmisClient` class. """

    def testCmisClient(self):
        '''Instantiate a CmisClient object'''
        cmisClient = CmisClient(REPOSITORY_URL, USERNAME, PASSWORD)
        self.assert_(cmisClient != None)

    def testGetRepositories(self):
        '''Call getRepositories and make sure at least one comes back with
        an ID and a name
        '''
        cmisClient = CmisClient(REPOSITORY_URL, USERNAME, PASSWORD)
        repoInfo = cmisClient.getRepositories()
        self.assert_(len(repoInfo) >= 1)
        self.assert_('repositoryId' in repoInfo[0])
        self.assert_('repositoryName' in repoInfo[0])

    def testDefaultRepository(self):
        '''Get the default repository by calling the repo's service URL'''
        cmisClient = CmisClient(REPOSITORY_URL, USERNAME, PASSWORD)
        repo = cmisClient.getDefaultRepository()
        self.assert_(repo != None)
        self.assert_(repo.getRepositoryId() != None)

    def testGetRepository(self):
        '''Get a repository by repository ID'''
        cmisClient = CmisClient(REPOSITORY_URL, USERNAME, PASSWORD)
        repo = cmisClient.getDefaultRepository()
        defaultRepoId = repo.getRepositoryId()
        defaultRepoName = repo.getRepositoryName()
        repo = cmisClient.getRepository(defaultRepoId)
        self.assertEquals(defaultRepoId, repo.getRepositoryId())
        self.assertEquals(defaultRepoName, repo.getRepositoryName())

    # Error conditions
    def testCmisClientBadUrl(self):
        '''Try to instantiate a CmisClient object with a known bad URL'''
        cmisClient = CmisClient(REPOSITORY_URL + 'foobar', USERNAME, PASSWORD)
        self.assertRaises(CmisException, cmisClient.getRepositories)

    def testCmisClientBadAuth(self):
        '''Try to instantiate a CmisClient object with bad creds'''
        cmisClient = CmisClient(REPOSITORY_URL, USERNAME, 'BADPASS')
        self.assertRaises(PermissionDeniedException,
                          cmisClient.getRepositories)

    def testGetRepositoryBadId(self):
        '''Try to get a repository with a bad repo ID'''
        cmisClient = CmisClient(REPOSITORY_URL, USERNAME, PASSWORD)
        self.assertRaises(ObjectNotFoundException,
                          cmisClient.getRepository,
                          '123FOO')


class QueryTest(CmisTestBase):

    """ Tests related to running CMIS queries. """

    # TODO: Test the rest of these queries
    #    queryDateRange = "SELECT cmis:name from cmis:document " \
    #                         "where cmis:creationDate >= TIMESTAMP'2009-11-10T00:00:00.000-06:00' and " \
    #                         "cmis:creationDate < TIMESTAMP'2009-11-18T00:00:00.000-06:00'"
    #    queryFolderFullText = "SELECT cmis:name from cmis:document " \
    #                              "where in_folder('workspace://SpacesStore/3935ce21-9f6f-4d46-9e22-4f97e1d5d9d8') " \
    #                              "and contains('contract')"
    #    queryCombined = "SELECT cmis:name from cmis:document " \
    #                        "where in_tree('workspace://SpacesStore/3935ce21-9f6f-4d46-9e22-4f97e1d5d9d8') and " \
    #                        "contains('contract') and cm:description like \"%sign%\""

    def setUp(self):
        """
        Override the base setUp to include creating a couple
        of test docs.
        """
        CmisTestBase.setUp(self)
        # I think this may be an Alfresco bug. The CMIS query results contain
        # 1 less entry element than the number of search results. So this test
        # will create two documents and search for the second one which should
        # work in all repositories.
        testFile = open('sample-a.pdf', 'rb')
        self._testContent = self._testFolder.createDocument(testFile.name, contentFile=testFile)
        testFile.close()
        testFile = open('sample-a.pdf', 'rb')
        self._testContent2 = self._testFolder.createDocument('sample-b.pdf', contentFile=testFile)
        testFile.close()
        self._maxFullTextTries = 10

    def testSimpleSelect(self):
        '''Execute simple select star from cmis:document'''
        querySimpleSelect = "SELECT * FROM cmis:document"
        resultSet = self._repo.query(querySimpleSelect)
        self.assertTrue(isInResultSet(resultSet, self._testContent))

    def testWildcardPropertyMatch(self):
        '''Find content w/wildcard match on cmis:name property'''
        querySimpleSelect = "SELECT * FROM cmis:document where cmis:name like '" + self._testContent.getProperties()['cmis:name'][:7] + "%'"
        resultSet = self._repo.query(querySimpleSelect)
        self.assertTrue(isInResultSet(resultSet, self._testContent))

    def testPropertyMatch(self):
        '''Find content matching cmis:name property'''
        querySimpleSelect = "SELECT * FROM cmis:document where cmis:name = '" + self._testContent2.getProperties()['cmis:name'] + "'"
        resultSet = self._repo.query(querySimpleSelect)
        self.assertTrue(isInResultSet(resultSet, self._testContent2))

    def testFullText(self):
        '''Find content using a full-text query'''
        queryFullText = "SELECT cmis:objectId, cmis:name FROM cmis:document " \
                        "WHERE contains('whitepaper')"
        # on the first full text search the indexer may need a chance to
        # do its thing
        found = False
        maxTries = self._maxFullTextTries
        while not found and (maxTries > 0):
            resultSet = self._repo.query(queryFullText)
            found = isInResultSet(resultSet, self._testContent2)
            if not found:
                maxTries -= 1
                print 'Not found...sleeping for 10 secs. Remaining tries:%d' % maxTries
                sleep(10)
        self.assertTrue(found)

    def testScore(self):
        '''Find content using FT, sorted by relevance score'''
        queryScore = "SELECT cmis:objectId, cmis:name, Score() as relevance " \
                     "FROM cmis:document WHERE contains('sample') " \
                     "order by relevance DESC"

        # on the first full text search the indexer may need a chance to
        # do its thing
        found = False
        maxTries = self._maxFullTextTries
        while not found and (maxTries > 0):
            resultSet = self._repo.query(queryScore)
            found = isInResultSet(resultSet, self._testContent2)
            if not found:
                maxTries -= 1
                print 'Not found...sleeping for 10 secs. Remaining tries:%d' % maxTries
                sleep(10)
        self.assertTrue(found)


class RepositoryTest(CmisTestBase):

    """ Tests for the :class:`Repository` class. """

    def testRepositoryInfo(self):
        '''Retrieve repository info'''
        repoInfo = self._repo.getRepositoryInfo()
        self.assertTrue('repositoryId' in repoInfo)
        self.assertTrue('repositoryName' in repoInfo)
        self.assertTrue('repositoryDescription' in repoInfo)
        self.assertTrue('vendorName' in repoInfo)
        self.assertTrue('productName' in repoInfo)
        self.assertTrue('productVersion' in repoInfo)
        self.assertTrue('rootFolderId' in repoInfo)
        self.assertTrue('cmisVersionSupported' in repoInfo)

    def testRepositoryCapabilities(self):
        '''Retrieve repository capabilities'''
        caps = self._repo.getCapabilities()
        self.assertTrue('ACL' in caps)
        self.assertTrue('AllVersionsSearchable' in caps)
        self.assertTrue('Changes' in caps)
        self.assertTrue('ContentStreamUpdatability' in caps)
        self.assertTrue('GetDescendants' in caps)
        self.assertTrue('GetFolderTree' in caps)
        self.assertTrue('Multifiling' in caps)
        self.assertTrue('PWCSearchable' in caps)
        self.assertTrue('PWCUpdatable' in caps)
        self.assertTrue('Query' in caps)
        self.assertTrue('Renditions' in caps)
        self.assertTrue('Unfiling' in caps)
        self.assertTrue('VersionSpecificFiling' in caps)
        self.assertTrue('Join' in caps)

    def testGetRootFolder(self):
        '''Get the root folder of the repository'''
        rootFolder = self._repo.getRootFolder()
        self.assert_(rootFolder != None)
        self.assert_(rootFolder.getObjectId() != None)

    def testCreateFolder(self):
        '''Create a new folder in the root folder'''
        folderName = 'testCreateFolder folder'
        newFolder = self._repo.createFolder(self._rootFolder, folderName)
        self.assertEquals(folderName, newFolder.getName())
        newFolder.delete()

    def testCreateDocument(self):
        '''Create a new 'content-less' document'''
        documentName = 'testDocument'
        newDoc = self._repo.createDocument(documentName, parentFolder=self._testFolder)
        self.assertEquals(documentName, newDoc.getName())

    def testGetObject(self):
        '''Create a test folder then attempt to retrieve it as a
        :class:`CmisObject` object using its object ID'''
        folderName = 'testGetObject folder'
        newFolder = self._repo.createFolder(self._testFolder, folderName)
        objectId = newFolder.getObjectId()
        someObject = self._repo.getObject(objectId)
        self.assertEquals(folderName, someObject.getName())
        newFolder.delete()

    def testGetFolder(self):
        '''Create a test folder then attempt to retrieve the Folder object
        using its object ID'''
        folderName = 'testGetFolder folder'
        newFolder = self._repo.createFolder(self._testFolder, folderName)
        objectId = newFolder.getObjectId()
        someFolder = self._repo.getFolder(objectId)
        self.assertEquals(folderName, someFolder.getName())
        newFolder.delete()

    def testGetObjectByPath(self):
        '''Create test objects (one folder, one document) then try to get
        them by path'''
        # names of folders and test docs
        testFolderName = self._testFolder.getName()
        parentFolderName = 'testGetObjectByPath folder'
        subFolderName = 'subfolder'
        docName = 'testdoc'

        # create the folder structure
        parentFolder = self._testFolder.createFolder(parentFolderName)
        subFolder = parentFolder.createFolder(subFolderName)
        searchFolder = self._repo.getObjectByPath("/".join(['', testFolderName, parentFolderName, subFolderName]))
        self.assertEquals(subFolder.getObjectId(), searchFolder.getObjectId())

        # create a test doc
        doc = subFolder.createDocument(docName)
        searchDoc = self._repo.getObjectByPath("/".join(['', testFolderName, parentFolderName, subFolderName, docName]))
        self.assertEquals(doc.getObjectId(), searchDoc.getObjectId())

        # get the subfolder by path, then ask for its children
        subFolder = self._repo.getObjectByPath("/".join(['', testFolderName, parentFolderName, subFolderName]))
        self.assertEquals(len(subFolder.getChildren().getResults()), 1)

    #Exceptions

    def testGetObjectBadId(self):
        '''Attempt to get an object using a known bad ID'''
        # this object ID is implementation specific (Alfresco) but is universally
        # bad so it should work for all repositories
        self.assertRaises(ObjectNotFoundException,
                          self._repo.getObject,
                          'workspace://SpacesStore/409f15e4-c8de-4ce1-9421-f95c4c064FOO')

    def testGetObjectBadPath(self):
        '''Attempt to get an object using a known bad path'''
        self.assertRaises(ObjectNotFoundException,
                          self._repo.getObjectByPath,
                          '/123foo/BAR.jtp')


class FolderTest(CmisTestBase):

    """ Tests for the :class:`Folder` class """

    def testGetChildren(self):
        '''Get the children of the test folder'''
        childFolderName1 = 'testchild1'
        childFolderName2 = 'testchild2'
        grandChildFolderName = 'testgrandchild'
        childFolder1 = self._testFolder.createFolder(childFolderName1)
        childFolder2 = self._testFolder.createFolder(childFolderName2)
        grandChild = childFolder2.createFolder(grandChildFolderName)
        resultSet = self._testFolder.getChildren()
        self.assert_(resultSet != None)
        self.assertEquals(2, len(resultSet.getResults()))
        self.assertTrue(isInResultSet(resultSet, childFolder1))
        self.assertTrue(isInResultSet(resultSet, childFolder2))
        self.assertFalse(isInResultSet(resultSet, grandChild))

    def testGetDescendants(self):
        '''Get the descendants of the root folder'''
        childFolderName1 = 'testchild1'
        childFolderName2 = 'testchild2'
        grandChildFolderName1 = 'testgrandchild'
        childFolder1 = self._testFolder.createFolder(childFolderName1)
        childFolder2 = self._testFolder.createFolder(childFolderName2)
        grandChild = childFolder1.createFolder(grandChildFolderName1)

        # test getting descendants with depth=1
        resultSet = self._testFolder.getDescendants(depth=1)
        self.assert_(resultSet != None)
        self.assertEquals(2, len(resultSet.getResults()))
        self.assertTrue(isInResultSet(resultSet, childFolder1))
        self.assertTrue(isInResultSet(resultSet, childFolder2))
        self.assertFalse(isInResultSet(resultSet, grandChild))

        # test getting descendants with depth=2
        resultSet = self._testFolder.getDescendants(depth=2)
        self.assert_(resultSet != None)
        self.assertEquals(3, len(resultSet.getResults()))
        self.assertTrue(isInResultSet(resultSet, childFolder1))
        self.assertTrue(isInResultSet(resultSet, childFolder2))
        self.assertTrue(isInResultSet(resultSet, grandChild))

        # test getting descendants with depth=-1
        resultSet = self._testFolder.getDescendants() #-1 is the default depth
        self.assert_(resultSet != None)
        self.assertEquals(3, len(resultSet.getResults()))
        self.assertTrue(isInResultSet(resultSet, childFolder1))
        self.assertTrue(isInResultSet(resultSet, childFolder2))
        self.assertTrue(isInResultSet(resultSet, grandChild))

    def testDeleteEmptyFolder(self):
        '''Create a test folder, then delete it'''
        folderName = 'testDeleteEmptyFolder folder'
        testFolder = self._testFolder.createFolder(folderName)
        self.assertEquals(folderName, testFolder.getName())
        newFolder = testFolder.createFolder('testFolder')
        testFolderChildren = testFolder.getChildren()
        self.assertEquals(1, len(testFolderChildren.getResults()))
        newFolder.delete()
        testFolderChildren = testFolder.getChildren()
        self.assertEquals(0, len(testFolderChildren.getResults()))

    def testDeleteNonEmptyFolder(self):
        '''Create a test folder with something in it, then delete it'''
        folderName = 'testDeleteNonEmptyFolder folder'
        testFolder = self._testFolder.createFolder(folderName)
        self.assertEquals(folderName, testFolder.getName())
        newFolder = testFolder.createFolder('testFolder')
        testFolderChildren = testFolder.getChildren()
        self.assertEquals(1, len(testFolderChildren.getResults()))
        newFolder.createDocument('testDoc')
        self.assertEquals(1, len(newFolder.getChildren().getResults()))
        newFolder.deleteTree()
        testFolderChildren = testFolder.getChildren()
        self.assertEquals(0, len(testFolderChildren.getResults()))

    def testGetProperties(self):
        '''Get the root folder, then get its properties'''
        props = self._testFolder.getProperties()
        self.assert_(props != None)
        self.assert_('cmis:objectId' in props)
        self.assert_(props['cmis:objectId'] != None)
        self.assert_('cmis:objectTypeId' in props)
        self.assert_(props['cmis:objectTypeId'] != None)
        self.assert_('cmis:name' in props)
        self.assert_(props['cmis:name'] != None)

    def testUpdateProperties(self):
        '''Create a test folder, then update its properties'''
        folderName = 'testUpdateProperties folder'
        newFolder = self._testFolder.createFolder(folderName)
        self.assertEquals(folderName, newFolder.getName())
        folderName2 = 'testUpdateProperties folder2'
        props = {'cmis:name': folderName2}
        newFolder.updateProperties(props)
        self.assertEquals(folderName2, newFolder.getName())

    def testSubFolder(self):
        '''Create a test folder, then create a test folder within that.'''
        parentFolder = self._testFolder.createFolder('testSubFolder folder')
        self.assert_('cmis:objectId' in parentFolder.getProperties())
        childFolder = parentFolder.createFolder('child folder')
        self.assert_('cmis:objectId' in childFolder.getProperties())
        self.assert_(childFolder.getProperties()['cmis:objectId'] != None)

    def testAllowableActions(self):
        '''Create a test folder, then get its allowable actions'''
        actions = self._testFolder.getAllowableActions()
        self.assert_(len(actions) > 0)

    # Exceptions

    def testBadParentFolder(self):
        '''Try to create a folder on a bad/bogus/deleted parent
        folder object'''
        firstFolder = self._testFolder.createFolder('testBadParentFolder folder')
        self.assert_('cmis:objectId' in firstFolder.getProperties())
        firstFolder.delete()
        # folder isn't in the repo anymore, but I still have the object
        # really, this seems like it ought to be an ObjectNotFoundException but
        # not all CMIS providers report it as such
        self.assertRaises(CmisException,
                          firstFolder.createFolder,
                          'bad parent')

    def testDuplicateFolder(self):
        '''Try to create a folder that already exists'''
        folderName = 'testDupFolder folder'
        firstFolder = self._testFolder.createFolder(folderName)
        self.assert_('cmis:objectId' in firstFolder.getProperties())
        # really, this needs to be ContentAlreadyExistsException but
        # not all CMIS providers report it as such
        self.assertRaises(CmisException,
                          self._testFolder.createFolder,
                          folderName)


class DocumentTest(CmisTestBase):

    """ Tests for the :class:`Document` class """

    def testCheckout(self):
        '''Create a document in a test folder, then check it out'''
        newDoc = self._testFolder.createDocument('testDocument')
        pwcDoc = newDoc.checkout()
        try:
            self.assertTrue(newDoc.isCheckedOut())
            self.assert_('cmis:objectId' in newDoc.getProperties())
            self.assert_('cmis:objectId' in pwcDoc.getProperties())
            checkedOutDocs = self._repo.getCollection('checkedout')
            self.assertTrue(isInResultSet(checkedOutDocs, pwcDoc))
        finally:
            pwcDoc.delete()

    def testCheckin(self):
        '''Create a document in a test folder, check it out, then in'''
        testFilename = '250px-Cmis_logo.png'
        contentFile = open(testFilename, 'rb')
        testDoc = self._testFolder.createDocument(testFilename, contentFile=contentFile)
        contentFile.close()
        self.assertEquals(testFilename, testDoc.getName())
        pwcDoc = testDoc.checkout()

        try:
            self.assertTrue(testDoc.isCheckedOut())
            self.assert_('cmis:objectId' in testDoc.getProperties())
            self.assert_('cmis:objectId' in pwcDoc.getProperties())
            testDoc = pwcDoc.checkin(checkinComment='Just a few changes')
            self.assertEquals('Just a few changes',
                          testDoc.getProperties()['cmis:checkinComment'])
            self.assertFalse(testDoc.isCheckedOut())
        finally:
            if testDoc.isCheckedOut():
                pwcDoc.delete()

    def testCheckinAfterGetPWC(self):
        '''Create a document in a test folder, check it out, call getPWC, then checkin'''
        testFilename = '250px-Cmis_logo.png'
        contentFile = open(testFilename, 'rb')
        testDoc = self._testFolder.createDocument(testFilename, contentFile=contentFile)
        contentFile.close()
        self.assertEquals(testFilename, testDoc.getName())
        # Alfresco has a bug where if you get the PWC this way
        # the checkin will not be successful
        testDoc.checkout()
        pwcDoc = testDoc.getPrivateWorkingCopy()
        try:
            self.assertTrue(testDoc.isCheckedOut())
            self.assert_('cmis:objectId' in testDoc.getProperties())
            self.assert_('cmis:objectId' in pwcDoc.getProperties())
            testDoc = pwcDoc.checkin(checkinComment='Just a few changes')
            self.assertFalse(testDoc.isCheckedOut())
            self.assertEquals('Just a few changes',
                          testDoc.getProperties()['cmis:checkinComment'])
        finally:
            if testDoc.isCheckedOut():
                pwcDoc.delete()

    def testCancelCheckout(self):
        '''Create a document in a test folder, check it out, then cancel
        checkout'''
        newDoc = self._testFolder.createDocument('testDocument')
        pwcDoc = newDoc.checkout()
        try:
            self.assertTrue(newDoc.isCheckedOut())
            self.assert_('cmis:objectId' in newDoc.getProperties())
            self.assert_('cmis:objectId' in pwcDoc.getProperties())
            checkedOutDocs = self._repo.getCollection('checkedout')
            self.assertTrue(isInResultSet(checkedOutDocs, pwcDoc))
        finally:
            pwcDoc.delete()
        self.assertFalse(newDoc.isCheckedOut())
        checkedOutDocs = self._repo.getCollection('checkedout')
        self.assertFalse(isInResultSet(checkedOutDocs, pwcDoc))

    def testDeleteDocument(self):
        '''Create a document in a test folder, then delete it'''
        newDoc = self._testFolder.createDocument('testDocument')
        children = self._testFolder.getChildren()
        self.assertEquals(1, len(children.getResults()))
        newDoc.delete()
        children = self._testFolder.getChildren()
        self.assertEquals(0, len(children.getResults()))

    def testGetProperties(self):
        '''Create a document in a test folder, then get its properties'''
        newDoc = self._testFolder.createDocument('testDocument')
        self.assertEquals('testDocument', newDoc.getName())
        self.assertTrue('cmis:objectTypeId' in newDoc.getProperties())
        self.assertTrue('cmis:objectId' in newDoc.getProperties())

    def testAllowableActions(self):
        '''Create document in a test folder, then get its allowable actions'''
        newDoc = self._testFolder.createDocument('testDocument')
        actions = newDoc.getAllowableActions()
        self.assert_(len(actions) > 0)

    def testUpdateProperties(self):
        '''Create a document in a test folder, then update its properties'''
        newDoc = self._testFolder.createDocument('testDocument')
        self.assertEquals('testDocument', newDoc.getName())
        props = {'cmis:name': 'testDocument2', 'cmis:versionLabel': 'foo'}
        newDoc.updateProperties(props)
        self.assertEquals('testDocument2', newDoc.getName())

    def testCreateDocumentBinary(self):
        ''' Create a document using a file from the file system '''
        testFilename = '250px-Cmis_logo.png'
        contentFile = open(testFilename, 'rb')
        newDoc = self._testFolder.createDocument(testFilename, contentFile=contentFile)
        contentFile.close()
        self.assertEquals(testFilename, newDoc.getName())

        # test to make sure the file we get back is the same length
        # as the file we sent
        result = newDoc.getContentStream()
        exportFilename = testFilename.replace('png', 'export.png')
        outfile = open(exportFilename, 'wb')
        outfile.write(result.read())
        result.close()
        outfile.close()
        self.assertEquals(os.path.getsize(testFilename),
                          os.path.getsize(exportFilename))

        # cleanup
        os.remove(exportFilename)

    def testCreateDocumentPlain(self):
        ''' Create a document using a file from the file system '''
        testFilename = 'plain.txt'
        testFile = open(testFilename, 'w')
        testFile.write('This is a sample text file line 1.\n')
        testFile.write('This is a sample text file line 2.\n')
        testFile.write('This is a sample text file line 3.\n')
        testFile.close()
        contentFile = open(testFilename, 'r')
        newDoc = self._testFolder.createDocument(testFilename, contentFile=contentFile)
        contentFile.close()
        self.assertEquals(testFilename, newDoc.getName())

        # test to make sure the file we get back is the same length as the
        # file we sent
        result = newDoc.getContentStream()
        exportFilename = testFilename.replace('txt', 'export.txt')
        outfile = open(exportFilename, 'w')
        outfile.write(result.read())
        result.close()
        outfile.close()
        self.assertEquals(os.path.getsize(testFilename),
                          os.path.getsize(exportFilename))

        # export
        os.remove(exportFilename)
        os.remove(testFilename)


class TypeTest(unittest.TestCase):

    """
    Tests for the :class:`ObjectType` class (and related methods in the
    :class:`Repository` class.
    """

    def testTypeDescendants(self):
        '''Get the descendant types of the repository.'''

        cmisClient = CmisClient(REPOSITORY_URL, USERNAME, PASSWORD)
        repo = cmisClient.getDefaultRepository()
        typeDefs = repo.getTypeDescendants()
        found = False
        for typeDef in typeDefs:
            if typeDef.getTypeId() == 'cmis:folder':
                found = True
                break
        self.assertTrue(found)

    def testTypeChildren(self):
        '''Get the child types for this repository and make sure cmis:folder
        is in the list.'''

        #This test would be more interesting if there was a standard way to
        #deploy a custom model. Then we could look for custom types.

        cmisClient = CmisClient(REPOSITORY_URL, USERNAME, PASSWORD)
        repo = cmisClient.getDefaultRepository()
        typeDefs = repo.getTypeChildren()
        found = False
        for typeDef in typeDefs:
            if typeDef.getTypeId() == 'cmis:folder':
                found = True
                break
        self.assertTrue(found)

    def testTypeDefinition(self):
        '''Get the cmis:document type and test a few props of the type.'''
        cmisClient = CmisClient(REPOSITORY_URL, USERNAME, PASSWORD)
        repo = cmisClient.getDefaultRepository()
        docTypeDef = repo.getTypeDefinition('cmis:document')
        self.assertEquals('cmis:document', docTypeDef.getTypeId())
        # Add some property inspection stuff here


def isInCollection(collection, targetDoc):
    '''
    Util function that searches a list of objects for a matching target
    object.
    '''
    for doc in collection:
        # hacking around a bizarre thing in Alfresco which is that when the
        # PWC comes back it has an object ID of say 123ABC but when you look
        # in the checked out collection the object ID of the PWC is now
        # 123ABC;1.0. What is that ;1.0? I don't know, but object IDs are
        # supposed to be immutable so I'm not sure what's going on there.
        if doc.getObjectId().startswith(targetDoc.getObjectId()):
            return True
    return False


def isInResultSet(resultSet, targetDoc):
    """
    Util function that searches a :class:`ResultSet` for a specified target
    object. Note that this function will do a getNext on every page of the
    result set until it finds what it is looking for or reaches the end of
    the result set. For every item in the result set, the properties
    are retrieved. Long story short: this could be an expensive call.
    """
    done = False
    while not done:
        for result in resultSet.getResults():
            if result.getObjectId().startswith(targetDoc.getObjectId()):
                return True
        if resultSet.hasNext():
            resultSet.getNext()
        else:
            done = True

if __name__ == "__main__":
    unittest.main()
