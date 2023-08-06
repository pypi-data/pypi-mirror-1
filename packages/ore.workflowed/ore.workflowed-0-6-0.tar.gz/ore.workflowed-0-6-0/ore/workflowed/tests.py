import unittest

from zope.testing import doctest
from zope import interface
from zope.app.testing import placelesssetup, ztapi

from ore.workflowed import interfaces, workflow
        
def workflowSetUp(doctest):
    placelesssetup.setUp()        
    ztapi.provideAdapter( interface.Interface, interfaces.IWorkflowInfo, workflow.WorkflowInfo )
    ztapi.provideAdapter( interface.Interface, interfaces.IWorkflowState, workflow.WorkflowState )
    
def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite(
            'readme.txt',
            setUp=workflowSetUp, tearDown=placelesssetup.tearDown,
            ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
