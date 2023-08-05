import unittest

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite

from zope.interface import implements, Interface
from zope.component import getUtility, getMultiAdapter

from zope.component.interfaces import IObjectEvent

from plone.contentrules.engine.interfaces import IRuleStorage
from plone.contentrules.rule.interfaces import IRuleCondition
from plone.contentrules.rule.interfaces import IExecutable

from plone.app.contentrules.rule import Rule

import collective.keywordcondition

from collective.keywordcondition.keyword import KeywordCondition
from collective.keywordcondition.keyword import KeywordEditForm

ptc.setupPloneSite()

class DummyEvent(object):
    implements(IObjectEvent)
    
    def __init__(self, obj):
        self.object = obj

# Since we do not need to quick-install anything or register a Zope 2 style
# product, we can use a simple layer that's set up after the Plone site has 
# been created above

class TestKeywordCondition(ptc.PloneTestCase):
    class layer(PloneSite):
        @classmethod
        def setUp(cls):
            fiveconfigure.debug_mode = True
            zcml.load_config('configure.zcml',
                             collective.keywordcondition)
            fiveconfigure.debug_mode = False

        @classmethod
        def tearDown(cls):
            pass

    def afterSetUp(self):
        self.setRoles(('Manager',))
        
    def testRegistered(self): 
        element = getUtility(IRuleCondition, name='collective.keywordcondition.Keyword')
        self.assertEquals('collective.keywordcondition.Keyword', element.addview)
        self.assertEquals('edit', element.editview)
        self.assertEquals(None, element.for_)
        self.assertEquals(IObjectEvent, element.event)
    
    def testInvokeAddView(self): 
        element = getUtility(IRuleCondition, name='collective.keywordcondition.Keyword')
        storage = getUtility(IRuleStorage)
        storage[u'foo'] = Rule()
        rule = self.portal.restrictedTraverse('++rule++foo')
        
        adding = getMultiAdapter((rule, self.portal.REQUEST), name='+condition')
        addview = getMultiAdapter((adding, self.portal.REQUEST), name=element.addview)
        
        addview.createAndAdd(data={'keywords' : ['Foo', 'Bar']})
        
        e = rule.conditions[0]
        self.failUnless(isinstance(e, KeywordCondition))
        self.assertEquals(['Foo', 'Bar'], e.keywords)
    
    def testInvokeEditView(self): 
        element = getUtility(IRuleCondition, name='collective.keywordcondition.Keyword')
        e = KeywordCondition()
        editview = getMultiAdapter((e, self.folder.REQUEST), name=element.editview)
        self.failUnless(isinstance(editview, KeywordEditForm))

    def testExecute(self): 
        e = KeywordCondition()
        e.keywords = ['Foo', 'Bar']
        
        self.folder.invokeFactory('Document', 'd1')
        self.folder.d1.setSubject(['Bar'])
        
        self.folder.invokeFactory('Document', 'd2')
        self.folder.d2.setSubject(['Baz'])
        
        ex = getMultiAdapter((self.portal, e, DummyEvent(self.folder.d1)), IExecutable)
        self.assertEquals(True, ex())
        
        ex = getMultiAdapter((self.portal, e, DummyEvent(self.folder.d2)), IExecutable)
        self.assertEquals(False, ex())

def test_suite():
    return unittest.TestSuite([
            unittest.makeSuite(TestKeywordCondition)
        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')