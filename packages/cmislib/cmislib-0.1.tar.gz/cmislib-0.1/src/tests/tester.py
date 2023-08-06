from unittest import TestSuite, TestResult, TestLoader
from tests.cmislibtest import CmisClientTest, QueryTest, FolderTest, DocumentTest, TypeTest, RepositoryTest

# Filenet working tests
# - TypeTest
# - RepositoryTest
# - FolderTest
# - CmisClientTest

# Filenet broken tests
# - QueryTest
#  - Depends on create document to be working
#  - Depends on Jay installing full-text
#  - Date range isn't working on Jay's side
# - DocumentTest
#  - testCheckout: will fail until checkedout contains PWC objects
#  - testCancelCheckout: will fail until checkedout contains PWC objects

tts = TestSuite()
#tts.addTest(FolderTest('testAllowableActions'))
#tts.addTest(DocumentTest('testAllowableActions'))
#tts = TestLoader().loadTestsFromTestCase(DocumentTest)
#tts = TestLoader().loadTestsFromTestCase(CmisClientTest)
tts.addTest(CmisClientTest('testGetRepository'))
tts.addTest(CmisClientTest('testDefaultRepository'))
#tts = TestLoader().loadTestsFromTestCase(QueryTest)
#tts = TestLoader().loadTestsFromTestCase(RepositoryTest)
#tts.addTest(QueryTest('testScore'))
#tts.addTest(QueryTest('testSimpleSelect'))
#tts.addTest(QueryTest('testWildcardPropertyMatch'))
#tts.addTest(DocumentTest('testCreateDocumentPlain'))
#tts.addTest(DocumentTest('testCreateDocumentBinary'))
#tts.addTest(FolderTest('testGetChildren'))
#tts.addTest(FolderTest('testGetDescendants'))
#tts.addTest(DocumentTest('testCheckout'))
#tts.addTest(DocumentTest('testCheckin'))
#tts.addTest(DocumentTest('testCheckinAfterGetPWC'))
#tts.addTest(DocumentTest('testCancelCheckout'))

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