# -*- coding: utf8 -*
""" Test suite for WorkflowField.
"""

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))


from Testing import ZopeTestCase
from Products.PloneTestCase import PloneTestCase
from Products.CMFPlone.utils import safe_hasattr, base_hasattr

PloneTestCase.installProduct('WorkflowField')

# Create plone site instance
PloneTestCase.setupPloneSite(
    extension_profiles=['Products.WorkflowField:exampletypes'])

class TestWorkflowField(PloneTestCase.PloneTestCase):
    """
    Test suite for WorkflowField.
    """

    def afterSetUp(self):
        self._createContent()

    def _createContent(self):
        """ Create content needed to run tests.
        """
        self.folder.invokeFactory(
            id='example1', 
            type_name='ExampleWFFieldContent')

    def testContentCreation(self):
        self.failUnless(base_hasattr(self.folder, 'example1'))

    def testTransition(self):
        obj = self.folder.example1
        wf_tool = self.portal.portal_workflow

        self.failUnlessEqual('private', 
            wf_tool.getInfoFor(obj, 'review_state'))

        obj.setReviewState('submit')
        self.failUnlessEqual('pending', 
            wf_tool.getInfoFor(obj, 'review_state'))

    def test_comments(self):
        obj = self.folder.example1
        obj.setReviewState('submit', comment='Please publish!')

        wf_tool = self.portal.portal_workflow
        history = wf_tool.getInfoFor(obj, 'review_history')
        self.failUnlessEqual('Please publish!', history[1]['comments'])

    def test_vocabulary(self):
        obj = self.folder.example1
        vocab = obj.getField('status').Vocabulary(obj)
        self.failUnlessEqual(vocab.items(), 
            (('private', 'Private'), ('submit', 'Submit for publication')))

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestWorkflowField))
    return suite

if __name__ == '__main__':
    framework()

