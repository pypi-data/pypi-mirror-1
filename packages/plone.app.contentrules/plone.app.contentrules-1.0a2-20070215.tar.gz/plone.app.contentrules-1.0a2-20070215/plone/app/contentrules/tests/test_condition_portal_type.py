from zope.interface import implements, Interface
from zope.component import getUtility, getMultiAdapter

from zope.component.interfaces import IObjectEvent

from plone.contentrules.engine.interfaces import IRuleStorage
from plone.contentrules.rule.interfaces import IRuleCondition
from plone.contentrules.rule.interfaces import IExecutable

from plone.app.contentrules.conditions.portaltype import PortalTypeCondition
from plone.app.contentrules.conditions.portaltype import PortalTypeEditForm

from plone.app.contentrules.rule import Rule

from plone.app.contentrules.tests.base import ContentRulesTestCase

class DummyEvent(object):
    implements(IObjectEvent)
    
    def __init__(self, obj):
        self.object = obj

class TestPortalTypeCondition(ContentRulesTestCase):

    def afterSetUp(self):
        self.setRoles(('Manager',))

    def testRegistered(self): 
        element = getUtility(IRuleCondition, name='plone.conditions.PortalType')
        self.assertEquals('plone.conditions.PortalType', element.addview)
        self.assertEquals('edit.html', element.editview)
        self.assertEquals(None, element.for_)
        self.assertEquals(IObjectEvent, element.event)
    
    def testInvokeAddView(self): 
        element = getUtility(IRuleCondition, name='plone.conditions.PortalType')
        storage = IRuleStorage(self.folder)
        storage[u'foo'] = Rule()
        rule = self.folder.restrictedTraverse('++rule++foo')
        
        adding = getMultiAdapter((rule, self.folder.REQUEST), name='+')
        addview = getMultiAdapter((adding, self.folder.REQUEST), name=element.addview)
        
        addview.createAndAdd(data={'portal_type' : 'Folder'})
        
        e = rule.elements[0].instance
        self.failUnless(isinstance(e, PortalTypeCondition))
        self.assertEquals('Folder', e.portal_type)
    
    def testInvokeEditView(self): 
        element = getUtility(IRuleCondition, name='plone.conditions.PortalType')
        e = PortalTypeCondition()
        editview = getMultiAdapter((e, self.folder.REQUEST), name=element.editview)
        self.failUnless(isinstance(editview, PortalTypeEditForm))

    def testExecute(self): 
        e = PortalTypeCondition()
        e.portal_type = 'Folder'        
        
        ex = getMultiAdapter((self.folder, e, DummyEvent(self.folder)), IExecutable)
        self.assertEquals(True, ex())
        
        ex = getMultiAdapter((self.portal, e, DummyEvent(self.portal)), IExecutable)
        self.assertEquals(False, ex())
        
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPortalTypeCondition))
    return suite
