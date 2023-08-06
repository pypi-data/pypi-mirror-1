from unittest import TestSuite, TestResult, TestLoader
from tests.cmislibtest import CmisClientTest, QueryTest, FolderTest, DocumentTest, TypeTest, RepositoryTest

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

tts = TestLoader().loadTestsFromTestCase(CmisClientTest)
tts = TestLoader().loadTestsFromTestCase(RepositoryTest)
tts = TestLoader().loadTestsFromTestCase(DocumentTest)
#tts = TestLoader().loadTestsFromTestCase(QueryTest)
#tts = TestLoader().loadTestsFromTestCase(FolderTest)
#tts = TestLoader().loadTestsFromTestCase(TypeTest)

#tts.addTest(CmisClientTest('testDefaultRepository'))
#tts.addTest(QueryTest('testScore'))
#tts.addTest(QueryTest('testSimpleSelect'))
#tts.addTest(QueryTest('testWildcardPropertyMatch'))
#tts.addTest(DocumentTest('testCreateDocumentPlain'))
#tts.addTest(DocumentTest('testCreateDocumentBinary'))
#tts.addTest(DocumentTest('testSetContentStreamDoc'))
#tts.addTest(DocumentTest('testSetContentStreamPWC'))
#tts.addTest(DocumentTest('testUpdateProperties'))
#tts.addTest(FolderTest('testGetChildren'))
#tts.addTest(FolderTest('testGetDescendants'))
#tts.addTest(FolderTest('testUpdateProperties'))
#tts.addTest(DocumentTest('testCheckout'))
#tts.addTest(DocumentTest('testCheckin'))
#tts.addTest(DocumentTest('testCheckinAfterGetPWC'))
#tts.addTest(DocumentTest('testCancelCheckout'))
#tts.addTest(DocumentTest('testAllowableActions'))
#tts.addTest(RepositoryTest('testReturnVersion'))
#tts.addTest(FolderTest('testGetTree'))

result = TestResult()
print "Running tests..."
tts.run(result)
if result.wasSuccessful():
    print "No errors or failures!"
else:
    print "Errors (%d):" % len(result.errors)
    for error in result.errors:
        print error
        
    print "Failures (%d):" % len(result.failures)    
    for failure in result.failures:
        print failure