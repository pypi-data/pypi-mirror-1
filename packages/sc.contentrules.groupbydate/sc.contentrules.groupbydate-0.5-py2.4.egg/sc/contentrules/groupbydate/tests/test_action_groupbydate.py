from zope.interface import implements, Interface
from zope.component import getUtility, getMultiAdapter

from plone.contentrules.engine.interfaces import IRuleStorage
from plone.contentrules.rule.interfaces import IRuleAction
from plone.contentrules.rule.interfaces import IExecutable

from sc.contentrules.groupbydate.actions.groupbydate import GroupByDateAction
from sc.contentrules.groupbydate.actions.groupbydate import GroupByDateEditForm

from plone.app.contentrules.rule import Rule

from sc.contentrules.groupbydate.tests.base import TestCase

from zope.component.interfaces import IObjectEvent

from Products.PloneTestCase.setup import default_user

from DateTime import DateTime

class DummyEvent(object):
    implements(IObjectEvent)
    
    def __init__(self, object):
        self.object = object

class TestGroupByDateAction(TestCase):

    def afterSetUp(self):
        self.loginAsPortalOwner()
        self.portal.invokeFactory('Folder', 'target')
        self.login(default_user)
        self.folder.invokeFactory('Document', 'd1')
        self.folder.d1.setEffectiveDate(DateTime('2009/04/22'))

    def testRegistered(self): 
        element = getUtility(IRuleAction, name='sc.contentrules.actions.groupbydate')
        self.assertEquals('sc.contentrules.actions.groupbydate', element.addview)
        self.assertEquals('edit', element.editview)
        self.assertEquals(None, element.for_)
        self.assertEquals(IObjectEvent, element.event)
    
    def testInvokeAddView(self): 
        element = getUtility(IRuleAction, name='sc.contentrules.actions.groupbydate')
        storage = getUtility(IRuleStorage)
        storage[u'foo'] = Rule()
        rule = self.portal.restrictedTraverse('++rule++foo')
        
        adding = getMultiAdapter((rule, self.portal.REQUEST), name='+action')
        addview = getMultiAdapter((adding, self.portal.REQUEST), name=element.addview)
        
        addview.createAndAdd(data={'base_folder' : '/target','structure':'ymd'})
        
        e = rule.actions[0]
        self.failUnless(isinstance(e, GroupByDateAction))
        self.assertEquals('/target', e.base_folder)
    
    def testInvokeEditView(self): 
        element = getUtility(IRuleAction, name='sc.contentrules.actions.groupbydate')
        e = GroupByDateAction()
        editview = getMultiAdapter((e, self.folder.REQUEST), name=element.editview)
        self.failUnless(isinstance(editview, GroupByDateEditForm))

    def testExecute(self): 
        e = GroupByDateAction()
        e.base_folder = '/target'
        
        ex = getMultiAdapter((self.folder, e, DummyEvent(self.folder.d1)), IExecutable)
        self.assertEquals(True, ex())
        
        self.failIf('d1' in self.folder.objectIds())
        target_folder = self.portal.unrestrictedTraverse('%s/2009/04/22' % e.base_folder[1:])
        self.failUnless('d1' in target_folder.objectIds())
        
    def testExecuteWithError(self): 
        e = GroupByDateAction()
        e.base_folder = '/dummy'
        
        ex = getMultiAdapter((self.folder, e, DummyEvent(self.folder.d1)), IExecutable)
        self.assertEquals(False, ex())
        
        self.failUnless('d1' in self.folder.objectIds())
        self.failIf('d1' in self.portal.target.objectIds())
        
    def testExecuteWithoutPermissionsOnTarget(self):
        self.setRoles(('Member',))
        
        e = GroupByDateAction()
        e.base_folder = '/target'
        
        ex = getMultiAdapter((self.folder, e, DummyEvent(self.folder.d1)), IExecutable)
        self.assertEquals(True, ex())
        
        self.failIf('d1' in self.folder.objectIds())
        target_folder = self.portal.unrestrictedTraverse('%s/2009/04/22' % e.base_folder[1:])
        self.failUnless('d1' in target_folder.objectIds())
        
    def testExecuteWithNamingConflict(self):
        self.setRoles(('Manager',))
        target_folder_path = '2009/04/22'.split('/')

        target_folder = self.portal.target        
        for folder in target_folder_path:
            if not folder in target_folder.objectIds():
                target_folder.invokeFactory('Folder',folder)
            target_folder = target_folder[folder]
        target_folder.invokeFactory('Document', 'd1')
        
        self.setRoles(('Member',))
        
        e = GroupByDateAction()
        e.base_folder = '/target'
        
        ex = getMultiAdapter((self.folder, e, DummyEvent(self.folder.d1)), IExecutable)
        self.assertEquals(True, ex())
        
        self.failIf('d1' in self.folder.objectIds())
        self.failUnless('d1' in target_folder.objectIds())
        self.failUnless('d1.1' in target_folder.objectIds())
        
    def testExecuteWithSameSourceAndTargetFolder(self):
        self.setRoles(('Manager',))
        target_folder_path = '2009/04/22'.split('/')
        
        target_folder = self.portal.target
        for folder in target_folder_path:
            if not folder in target_folder.objectIds():
                target_folder.invokeFactory('Folder',folder)
            target_folder = target_folder[folder]
        
        target_folder.invokeFactory('Document', 'd1')
        target_folder.d1.setEffectiveDate(DateTime('2009/04/22'))
        
        e = GroupByDateAction()
        e.base_folder = '/target'
        
        ex = getMultiAdapter((target_folder, e, DummyEvent(target_folder.d1)), IExecutable)
        self.assertEquals(True, ex())
        
        self.assertEquals(['d1'], list(target_folder.objectIds()))
        
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestGroupByDateAction))
    return suite
