from unittest import TestSuite, TestResult, TestLoader, TextTestRunner
from tests.cmislibtest import CmisClientTest, QueryTest, FolderTest, \
        DocumentTest, TypeTest, RepositoryTest, ACLTest, ChangeEntryTest

# Nuxeo working tests
# - CmisClientTest
# - RepositoryTest
# - TypeTest (except testTypeDescendants

# Nuxeo broken tests
# - TypeTest.testTypeDescendants is broken because the typedescendants rel has the wrong type
#
# QUERY
# - QueryTests fail b/c Nuxeo parser is case-sensitive. Nuxeo to fix.
#
# FOLDER
# FolderTest.testAllowableActions : not yet implemented by Nuxeo
# FolderTest.testDuplicateFolder : asked Nuxeo if duplicate folders are okay. If so, need to remove my test.
#
# DOCUMENT
#DocumentTest.testCancelCheckout: Error 500, waiting to see if checkout prob fixes
#DocumentTest.testCheckin: Error 500, waiting to see if checkout prob fixes
#DocumentTest.testCheckinAfterGetPW: Error 500, waiting to see if checkout prob fixes
#DocumentTest.testCheckout: Error 500 reported to Nuxeo
#DocumentTest.testCreateDocumentBinar: no enclosure link, reported to Nuxeo
#DocumentTest.testCreateDocumentPlain: no enclosure link, reported to Nuxeo
#DocumentTest.testAllowableActions: Same as folder allowable actions

tts = TestSuite()

tts.addTests(TestLoader().loadTestsFromTestCase(CmisClientTest))
tts.addTests(TestLoader().loadTestsFromTestCase(RepositoryTest))
tts.addTests(TestLoader().loadTestsFromTestCase(FolderTest))
tts.addTests(TestLoader().loadTestsFromTestCase(DocumentTest))
tts.addTests(TestLoader().loadTestsFromTestCase(TypeTest))
tts.addTests(TestLoader().loadTestsFromTestCase(ACLTest))
tts.addTests(TestLoader().loadTestsFromTestCase(ChangeEntryTest))

#tts = TestLoader().loadTestsFromTestCase(QueryTest)

#tts.addTest(CmisClientTest('testDefaultRepository'))
#tts.addTest(QueryTest('testScore'))
#tts.addTest(QueryTest('testSimpleSelect'))
#tts.addTest(QueryTest('testWildcardPropertyMatch'))
#tts.addTest(DocumentTest('testCreateDocumentPlain'))
#tts.addTest(DocumentTest('testCreateDocumentBinary'))
#tts.addTest(DocumentTest('testSetContentStreamDoc'))
#tts.addTest(DocumentTest('testSetContentStreamPWC'))
#tts.addTest(DocumentTest('testCheckin'))
#tts.addTest(DocumentTest('testCheckinComment'))
#tts.addTest(DocumentTest('testCheckinAfterGetPWC'))
#tts.addTest(DocumentTest('testUpdateProperties'))
#tts.addTest(FolderTest('testGetChildren'))
#tts.addTest(FolderTest('testGetDescendants'))
#tts.addTest(FolderTest('testGetProperties'))
#tts.addTest(FolderTest('testUpdateProperties'))
#tts.addTest(DocumentTest('testCheckout'))
#tts.addTest(DocumentTest('testCheckin'))
#tts.addTest(DocumentTest('testCheckinAfterGetPWC'))
#tts.addTest(DocumentTest('testCancelCheckout'))
#tts.addTest(DocumentTest('testAllowableActions'))
#tts.addTest(RepositoryTest('testReturnVersion'))
#tts.addTest(TypeTest('testTypeDefinition'))
#tts.addTest(TypeTest('testTypeDescendants'))
#tts.addTest(FolderTest('testGetTree'))
#tts.addTest(ChangeEntryTest('testGetContentChanges'))
#tts.addTest(ChangeEntryTest('testGetProperties'))
#tts.addTest(ChangeEntryTest('testGetACL'))
            
ttr = TextTestRunner()
ttr.run(tts)