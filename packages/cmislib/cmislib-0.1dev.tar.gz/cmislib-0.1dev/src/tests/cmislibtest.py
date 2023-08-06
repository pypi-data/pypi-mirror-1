#
# Copyright 2009 Optaros, Inc.
#
'''
Unit tests for cmislib
'''
import unittest
from cmislib.model import CmisClient, \
                          ObjectNotFoundException, \
                          PermissionDeniedException, \
                          RuntimeException
import os
from time import sleep, time

#TODO: Move these out into a config file or something
#REPOSITORY_URL = 'http://cmis.alfresco.com/s/cmis'
REPOSITORY_URL = 'http://localhost:8080/alfresco/s/cmis'
USERNAME = 'admin'
PASSWORD = 'admin'


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
        self._testFolder.delete()    


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

    # Error conditions
    def testCmisClientBadUrl(self):
        '''Try to instantiate a CmisClient object with a known bad URL'''
        cmisClient = CmisClient(REPOSITORY_URL + 'foobar', USERNAME, PASSWORD)
        self.assertRaises(ObjectNotFoundException, cmisClient.getRepositories)

    def testCmisClientBadAuth(self):
        '''Try to instantiate a CmisClient object with bad creds'''
        cmisClient = CmisClient(REPOSITORY_URL, USERNAME, 'BADPASS')
        self.assertRaises(PermissionDeniedException,
                          cmisClient.getRepositories)


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
        self.assert_(rootFolder._objectId != None)

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

    def testQuery(self):
        '''Execute some test queries against test content'''
        querySimpleSelect = "SELECT * FROM cmis:document"
        queryFullText = "SELECT cmis:objectId, cmis:name FROM cmis:document " \
                        "WHERE contains('whitepaper')"
        queryScore = "SELECT cmis:objectId, cmis:name, Score() as relevance " \
                     "FROM cmis:document WHERE contains('sample') " \
                     "order by relevance DESC"
        
        '''
        TODO: Test the rest of these queries
        
        queryDateRange = "SELECT cmis:name from cmis:document " \
                         "where cmis:creationDate >= '2009-11-10T00:00:00.000-06:00' and " \
                         "cmis:creationDate < '2009-11-18T00:00:00.000-06:00'"
        queryFolderFullText = "SELECT cmis:name from cmis:document " \
                              "where in_folder('workspace://SpacesStore/3935ce21-9f6f-4d46-9e22-4f97e1d5d9d8') " \
                              "and contains('contract')"
        queryCombined = "SELECT cmis:name from cmis:document " \
                        "where in_tree('workspace://SpacesStore/3935ce21-9f6f-4d46-9e22-4f97e1d5d9d8') and " \
                        "contains('contract') and cm:description like \"%sign%\""
        '''

        # I think this may be an Alfresco bug. The CMIS query results contain
        # 1 less entry element than the number of search results. So this test
        # will create two documents and search for the second one which should
        # work in all repositories.
        testFile = open('sample-a.pdf', 'rb')
        testContent = self._testFolder.createDocument(testFile.name, contentFile=testFile)
        testFile.close()
        testFile = open('sample-a.pdf', 'rb')
        testContent2 = self._testFolder.createDocument('sample-b.pdf', contentFile=testFile)
        testFile.close()

        #testContent = repo.getObject('workspace://SpacesStore/90cf6342-9ea3-4bac-a4fb-6cb4d6609118')
        results = self._repo.query(querySimpleSelect)
        self.assertTrue(isInCollection(results, testContent))
        print '\n\tSimple select is ok'

        # on the first full text search the indexer needs a chance to
        # do its thing
        found = False
        maxTries = 10
        while not found and (maxTries > 0):
            results = self._repo.query(queryFullText)
            found = isInCollection(results, testContent2)
            if not found:
                maxTries -= 1
                print 'Not found...sleeping for 10 secs. Remaining tries:%d' % maxTries
                sleep(10)
        self.assertTrue(found)
        print '\tFull text is ok'

        results = self._repo.query(queryScore)
        self.assertTrue(isInCollection(results, testContent2))
        print '\tRelevance score is ok'

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
        searchFolder = self._repo.getObjectByPath("/".join(['',testFolderName, parentFolderName, subFolderName]))
        self.assertEquals(subFolder.getObjectId(), searchFolder.getObjectId())

        # create a test doc
        doc = subFolder.createDocument(docName)
        searchDoc = self._repo.getObjectByPath("/".join(['',testFolderName, parentFolderName, subFolderName, docName]))
        self.assertEquals(doc.getObjectId(), searchDoc.getObjectId())

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
        children = self._testFolder.getChildren()        
        self.assert_(children != None)
        self.assertEquals(2, len(children))
        self.assertTrue(isInCollection(children, childFolder1))
        self.assertTrue(isInCollection(children, childFolder2))
        self.assertFalse(isInCollection(children, grandChild))        

    def testGetDescendants(self):
        '''Get the descendants of the root folder'''
        childFolderName1 = 'testchild1'
        childFolderName2 = 'testchild2'
        grandChildFolderName1 = 'testgrandchild'
        childFolder1 = self._testFolder.createFolder(childFolderName1)
        childFolder2 = self._testFolder.createFolder(childFolderName2)
        grandChild = childFolder1.createFolder(grandChildFolderName1)
        descendants = self._testFolder.getDescendants()        
        self.assert_(descendants != None)
        # Right now this will behave exactly like getChildren
        # because I haven't implemented the depth argument        
        self.assertEquals(2, len(descendants))
        self.assertTrue(isInCollection(descendants, childFolder1))
        self.assertTrue(isInCollection(descendants, childFolder2))
        # See note above: eventually this needs to be assertTrue
        self.assertFalse(isInCollection(descendants, grandChild))
        
    def testDeleteFolder(self):
        '''Create a test folder, then delete it'''
        folderName = 'testDeleteFolder folder'
        testFolder = self._testFolder.createFolder(folderName)
        self.assertEquals(folderName, testFolder.getName())
        newFolder = testFolder.createFolder('testFolder')
        testFolderChildren = testFolder.getChildren()
        self.assertEquals(1, len(testFolderChildren))
        newFolder.delete()
        testFolderChildren = testFolder.getChildren()
        self.assertEquals(0, len(testFolderChildren))

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

    # Exceptions

    def testBadParentFolder(self):
        '''Try to create a folder on a bad/bogus/deleted parent
        folder object'''
        firstFolder = self._testFolder.createFolder('testBadParentFolder folder')
        self.assert_('cmis:objectId' in firstFolder.getProperties())
        firstFolder.delete()
        # folder isn't in the repo anymore, but I still have the object
        self.assertRaises(ObjectNotFoundException,
                          firstFolder.createFolder,
                          'bad parent')

    def testDuplicateFolder(self):
        '''Try to create a folder that already exists'''
        folderName = 'testDupFolder folder'
        firstFolder = self._testFolder.createFolder(folderName)
        self.assert_('cmis:objectId' in firstFolder.getProperties())
        # really, this needs to be ContentAlreadyExistsException but
        # not all CMIS providers report it as such
        self.assertRaises(RuntimeException,
                          self._testFolder.createFolder,
                          folderName)


class DocumentTest(CmisTestBase):

    """ Tests for the :class:`Document` class """

    def testCheckout(self):
        '''Create a document in a test folder, then check it out'''
        newDoc = self._testFolder.createDocument('testDocument')
        pwcDoc = newDoc.checkout()
        try:
            self.assert_('cmis:objectId' in newDoc.getProperties())
            self.assert_('cmis:objectId' in pwcDoc.getProperties())
            checkedOutDocs = self._repo.getCollection('checkedout')
            self.assertTrue(isInCollection(checkedOutDocs, pwcDoc))
        finally:
            pwcDoc.delete()

    def testCheckin(self):
        '''Create a document in a test folder, check it out,
        then check it in'''
        testDoc = self._testFolder.createDocument('testDocument')
        pwcDoc = testDoc.checkout()
        try:        
            self.assert_('cmis:objectId' in testDoc.getProperties())
            self.assert_('cmis:objectId' in pwcDoc.getProperties())
            testDoc = pwcDoc.checkin(checkinComment='Just a few changes')
            self.assertEquals('Just a few changes',
                          testDoc.getProperties()['cmis:checkinComment'])
        except Exception:
            pwcDoc.delete()                

    def testCancelCheckout(self):
        '''Create a document in a test folder, check it out, then cancel
        checkout'''
        newDoc = self._testFolder.createDocument('testDocument')
        pwcDoc = newDoc.checkout()
        try:
            self.assert_('cmis:objectId' in newDoc.getProperties())
            self.assert_('cmis:objectId' in pwcDoc.getProperties())
            checkedOutDocs = self._repo.getCollection('checkedout')
            self.assertTrue(isInCollection(checkedOutDocs, pwcDoc))
        finally:
            pwcDoc.delete()
        checkedOutDocs = self._repo.getCollection('checkedout')
        self.assertFalse(isInCollection(checkedOutDocs, pwcDoc))

    def testDeleteDocument(self):
        '''Create a document in a test folder, then delete it'''
        newDoc = self._testFolder.createDocument('testDocument')
        children = self._testFolder.getChildren()
        self.assertEquals(1, len(children))
        newDoc.delete()
        children = self._testFolder.getChildren()
        self.assertEquals(0, len(children))

    def testGetProperties(self):
        '''Create a document in a test folder, then get its properties'''
        newDoc = self._testFolder.createDocument('testDocument')
        self.assertEquals('testDocument', newDoc.getName())
        self.assertTrue('cmis:objectTypeId' in newDoc.getProperties())
        self.assertTrue('cmis:objectId' in newDoc.getProperties())

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
        
        '''
        This test would be more interesting if there was a standard way to
        deploy a custom model. Then we could look for custom types.
        '''
        
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
        
        '''
        This test would be more interesting if there was a standard way to
        deploy a custom model. Then we could look for custom types.
        '''
        
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
    Until I make it easier to find docs in a collection (like making it a
    dict on id or something)
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

if __name__ == "__main__":
    unittest.main()
    
