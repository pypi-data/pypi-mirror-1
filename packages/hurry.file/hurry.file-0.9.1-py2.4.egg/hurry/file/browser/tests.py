import unittest

from zope.testing import doctest
from zope.app.testing import placelesssetup
        
def workflowSetUp(doctest):
    placelesssetup.setUp()
    
def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite(
            'file.txt',
            setUp=workflowSetUp, tearDown=placelesssetup.tearDown,
            ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

