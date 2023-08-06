import unittest

from zope.component import provideHandler
import zope.component.testing

from AccessControl.PermissionRole import rolesForPermissionOn

from Products.CMFCore.testing import TraversingEventZCMLLayer
from Products.CMFCore.tests.base.dummy import DummyContent
from Products.CMFCore.tests.base.dummy import DummySite
from Products.CMFCore.tests.base.dummy import DummyTool
from Products.CMFCore.WorkflowTool import WorkflowTool

from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition

from collective.subtractiveworkflow.workflow import SubtractiveWorkflowDefinition
from collective.subtractiveworkflow import react

class SubtractiveWorkflowStandaloneTests(unittest.TestCase):

    layer = TraversingEventZCMLLayer

    def setUp(self):
        self.site = DummySite('site')
        self.site._setObject('portal_types', DummyTool())
        self.site._setObject('portal_workflow', WorkflowTool())
        self._constructDummyWorkflow()
        
        provideHandler(react.object_transitioned)
    
    def tearDown(self):
        zope.component.testing.tearDown()
    
    def _constructDummyWorkflow(self):
        
        wftool = self.site.portal_workflow
        wftool._setObject('wf', SubtractiveWorkflowDefinition('wf'))
        wftool.setDefaultChain('wf')
        wf = wftool.wf

        wf.permissions = ('View',)

        wf.states.addState('nonconfidential')
        sdef = wf.states['nonconfidential']
        sdef.setProperties( transitions=('make_confidential',) )
        sdef.permission_roles = {'View': (),}

        wf.states.addState('confidential')
        sdef = wf.states['confidential']
        sdef.setProperties( transitions=('make_non_confidential',) )
        sdef.permission_roles = {'View': ('Anonymous', 'Authenticated',),}
        
        wf.states.setInitialState('nonconfidential')

        wf.transitions.addTransition('make_confidential')
        tdef = wf.transitions['make_confidential']
        tdef.setProperties(title='', new_state_id='confidential', actbox_name='')
        
        wf.transitions.addTransition('make_non_confidential')
        tdef = wf.transitions['make_non_confidential']
        tdef.setProperties(title='', new_state_id='nonconfidential', actbox_name='')

        wf.variables.addVariable('comments')
        vdef = wf.variables['comments']
        vdef.setProperties(description='',
                 default_expr="python:state_change.kwargs.get('comment', '')",
                 for_status=1, update_always=1)

    def _getDummyWorkflow(self):
        wftool = self.site.portal_workflow
        return wftool.wf

    def test_doActionFor_mixture(self):

        wftool = self.site.portal_workflow
        wf = self._getDummyWorkflow()
        
        # This time, disallow Authenticated and Manager
        wf.states['confidential'].permission_roles = {'View': ('Authenticated', 'Manager'),}
        
        dummy = self.site._setObject( 'dummy', DummyContent() )
        
        # These are the roles we know about
        self.assertEquals(['Anonymous', 'Authenticated', 'Manager', 'Owner'], sorted(dummy.validRoles()))
        
        # Now, if the item is normally granted to these roles
        dummy.manage_permission('View', ['Authenticated', 'Manager', 'Owner',], acquire=1)
        
        wftool.notifyCreated(dummy)
        self.assertEqual( wf._getStatusOf(dummy),
                          {'state': 'nonconfidential', 'comments': ''} )
        
        # Then in the non-confidential state (no permissions ticked) we still have that role
        self.assertEquals(['Authenticated', 'Manager', 'Owner'], sorted(rolesForPermissionOn('View', dummy)))
                          
        wf.doActionFor(dummy, 'make_confidential', comment='foo' )
        self.assertEqual( wf._getStatusOf(dummy),
                          {'state': 'confidential', 'comments': 'foo'} )
        
        # But after moving to confidential, which disallows Anonymous and Authenticated,
        # we are left with Owner and Manager
        self.assertEquals(['Owner'], sorted(rolesForPermissionOn('View', dummy)))

    def test_doActionFor_anonymous(self):

        wftool = self.site.portal_workflow
        wf = self._getDummyWorkflow()

        dummy = self.site._setObject( 'dummy', DummyContent() )
        
        # These are the roles we know about
        self.assertEquals(['Anonymous', 'Authenticated', 'Manager', 'Owner'], sorted(dummy.validRoles()))
        
        # Now, if the item is normally granted to anonymous...
        dummy.manage_permission('View', ['Anonymous'], acquire=1)
        
        wftool.notifyCreated(dummy)
        self.assertEqual( wf._getStatusOf(dummy),
                          {'state': 'nonconfidential', 'comments': ''} )
        
        # Then in the non-confidential state (no permissions ticked) we still have that role
        self.assertEquals(['Anonymous'], sorted(rolesForPermissionOn('View', dummy)))
                          
        wf.doActionFor(dummy, 'make_confidential', comment='foo' )
        self.assertEqual( wf._getStatusOf(dummy),
                          {'state': 'confidential', 'comments': 'foo'} )
        
        # But after moving to confidential, which disallows Anonymous and Authenticated,
        # we are left with Owner and Manager
        self.assertEquals(['Manager', 'Owner'], sorted(rolesForPermissionOn('View', dummy)))

class SubtractiveWorkflowSecondaryTests(unittest.TestCase):

    layer = TraversingEventZCMLLayer

    def setUp(self):
        self.site = DummySite('site')
        self.site._setObject('portal_types', DummyTool())
        self.site._setObject('portal_workflow', WorkflowTool())
        self._constructDummyWorkflows()
        
        provideHandler(react.object_transitioned)
    
    def tearDown(self):
        # zope.component.testing.tearDown()
        pass
    
    def _constructDummyWorkflows(self):
        
        wftool = self.site.portal_workflow
        wftool._setObject('wf1', DCWorkflowDefinition('wf1'))
        wftool._setObject('wf2', SubtractiveWorkflowDefinition('wf2'))
        
        wftool.setDefaultChain('wf1, wf2')
        wf1 = wftool.wf1
        wf2 = wftool.wf2

        # First workflow - private/published

        wf1.permissions = ('View',)
        
        wf1.states.addState('private')
        sdef = wf1.states['private']
        sdef.setProperties( transitions=('publish',) )
        sdef.permission_roles = {'View': ('Owner', 'Manager'),}

        wf1.states.addState('published')
        sdef = wf1.states['published']
        sdef.permission_roles = {'View': ('Anonymous',),}
        
        wf1.states.setInitialState('private')

        wf1.transitions.addTransition('publish')
        tdef = wf1.transitions['publish']
        tdef.setProperties(title='', new_state_id='published', actbox_name='')

        wf1.variables.addVariable('comments')
        vdef = wf1.variables['comments']
        vdef.setProperties(description='',
                 default_expr="python:state_change.kwargs.get('comment', '')",
                 for_status=1, update_always=1)

        # Second workflow - subtractive confidential/non-confidential
        
        wf2.permissions = ('View',)

        wf2.states.addState('nonconfidential')
        sdef = wf2.states['nonconfidential']
        sdef.setProperties( transitions=('make_confidential',) )
        sdef.permission_roles = {'View': (),}

        wf2.states.addState('confidential')
        sdef = wf2.states['confidential']
        sdef.setProperties( transitions=('make_non_confidential',) )
        sdef.permission_roles = {'View': ('Anonymous', 'Authenticated',),}
        
        wf2.states.setInitialState('nonconfidential')

        wf2.transitions.addTransition('make_confidential')
        tdef = wf2.transitions['make_confidential']
        tdef.setProperties(title='', new_state_id='confidential', actbox_name='')
        
        wf2.transitions.addTransition('make_non_confidential')
        tdef = wf2.transitions['make_non_confidential']
        tdef.setProperties(title='', new_state_id='nonconfidential', actbox_name='')

        wf2.variables.addVariable('comments')
        vdef = wf2.variables['comments']
        vdef.setProperties(description='',
                 default_expr="python:state_change.kwargs.get('comment', '')",
                 for_status=1, update_always=1)

    def _getDummyWorkflows(self):
        wftool = self.site.portal_workflow
        return (wftool.wf1, wftool.wf2,)

    def test_no_permissions_no_change(self):

        wftool = self.site.portal_workflow
        wf1, wf2 = self._getDummyWorkflows()
        
        dummy = self.site._setObject( 'dummy', DummyContent() )
        
        # These are the roles we know about
        self.assertEquals(['Anonymous', 'Authenticated', 'Manager', 'Owner'], sorted(dummy.validRoles()))
        
        # Now, if the item is normally granted to anonymous
        dummy.manage_permission('View', ['Anonymous',], acquire=1)
        
        wftool.notifyCreated(dummy)
        self.assertEqual( wf1._getStatusOf(dummy),
                          {'state': 'private', 'comments': ''} )
        self.assertEqual( wf2._getStatusOf(dummy),
                          {'state': 'nonconfidential', 'comments': ''} )
        
        # When private and non-confidential, manager and owner have the permission
        self.assertEquals(['Manager', 'Owner'], sorted(rolesForPermissionOn('View', dummy)))
                          
        wftool.doActionFor(dummy, 'publish', comment='foo' )
        self.assertEqual( wf1._getStatusOf(dummy),
                          {'state': 'published', 'comments': 'foo'} )
        self.assertEqual( wf2._getStatusOf(dummy),
                          {'state': 'nonconfidential', 'comments': ''} )
        
        # The item is now accessible to anonymous
        self.assertEquals(['Anonymous'], sorted(rolesForPermissionOn('View', dummy)))

    def test_with_permissions_subtracts(self):
        
        wftool = self.site.portal_workflow
        wf1, wf2 = self._getDummyWorkflows()
        
        dummy = self.site._setObject( 'dummy', DummyContent() )
        
        # These are the roles we know about
        self.assertEquals(['Anonymous', 'Authenticated', 'Manager', 'Owner'], sorted(dummy.validRoles()))
        
        # Now, if the item is normally granted to anonymous
        dummy.manage_permission('View', ['Anonymous',], acquire=1)
        
        wftool.notifyCreated(dummy)
        self.assertEqual( wf1._getStatusOf(dummy),
                          {'state': 'private', 'comments': ''} )
        self.assertEqual( wf2._getStatusOf(dummy),
                          {'state': 'nonconfidential', 'comments': ''} )
        
        # When private and non-confidential, manager and owner have the permission
        self.assertEquals(['Manager', 'Owner'], sorted(rolesForPermissionOn('View', dummy)))
                          
        wftool.doActionFor(dummy, 'publish', comment='foo' )
        self.assertEqual( wf1._getStatusOf(dummy),
                          {'state': 'published', 'comments': 'foo'} )
        self.assertEqual( wf2._getStatusOf(dummy),
                          {'state': 'nonconfidential', 'comments': ''} )
        
        # The item is now accessible to anonymous
        self.assertEquals(['Anonymous'], sorted(rolesForPermissionOn('View', dummy)))
        
        # Then let's make it confidential
        wftool.doActionFor(dummy, 'make_confidential', comment='bar' )
        self.assertEqual( wf1._getStatusOf(dummy),
                          {'state': 'published', 'comments': 'foo'} )
        self.assertEqual( wf2._getStatusOf(dummy),
                          {'state': 'confidential', 'comments': 'bar'} )
        
        # The item is no longer accessible to roles that are being subtracted
        self.assertEquals(['Manager', 'Owner'], sorted(rolesForPermissionOn('View', dummy)))
    
    def test_with_permissions_reacts(self):
        
        wftool = self.site.portal_workflow
        wf1, wf2 = self._getDummyWorkflows()
        
        dummy = self.site._setObject( 'dummy', DummyContent() )
        
        # These are the roles we know about
        self.assertEquals(['Anonymous', 'Authenticated', 'Manager', 'Owner'], sorted(dummy.validRoles()))
        
        # Now, if the item is normally granted to anonymous
        dummy.manage_permission('View', ['Anonymous',], acquire=1)
        
        wftool.notifyCreated(dummy)
        self.assertEqual( wf1._getStatusOf(dummy),
                          {'state': 'private', 'comments': ''} )
        self.assertEqual( wf2._getStatusOf(dummy),
                          {'state': 'nonconfidential', 'comments': ''} )
        
        # When private and non-confidential, manager and owner have the permission
        self.assertEquals(['Manager', 'Owner'], sorted(rolesForPermissionOn('View', dummy)))
        
        # Let's make it confidential too
        
        wftool.doActionFor(dummy, 'make_confidential', comment='bar')
        self.assertEqual( wf1._getStatusOf(dummy),
                          {'state': 'private', 'comments': ''} )
        self.assertEqual( wf2._getStatusOf(dummy),
                          {'state': 'confidential', 'comments': 'bar'} )
        
        # If we now publish it, the result should be the same as if we'd
        # published first and then made
        
        wftool.doActionFor(dummy, 'publish', comment='foo' )
        self.assertEqual( wf1._getStatusOf(dummy),
                          {'state': 'published', 'comments': 'foo'} )
        self.assertEqual( wf2._getStatusOf(dummy),
                          {'state': 'confidential', 'comments': 'bar'} )
        
        self.assertEquals(['Manager', 'Owner'], sorted(rolesForPermissionOn('View', dummy)))
    
    def test_undo(self):
        
        wftool = self.site.portal_workflow
        wf1, wf2 = self._getDummyWorkflows()
        
        dummy = self.site._setObject( 'dummy', DummyContent() )
        
        # These are the roles we know about
        self.assertEquals(['Anonymous', 'Authenticated', 'Manager', 'Owner'], sorted(dummy.validRoles()))
        
        # Now, if the item is normally granted to anonymous
        dummy.manage_permission('View', ['Anonymous',], acquire=1)
        
        wftool.notifyCreated(dummy)
        self.assertEqual( wf1._getStatusOf(dummy),
                          {'state': 'private', 'comments': ''} )
        self.assertEqual( wf2._getStatusOf(dummy),
                          {'state': 'nonconfidential', 'comments': ''} )
        
        # When private and non-confidential, manager and owner have the permission
        self.assertEquals(['Manager', 'Owner'], sorted(rolesForPermissionOn('View', dummy)))
        
        # Let's make it confidential too
        
        wftool.doActionFor(dummy, 'make_confidential', comment='bar')
        self.assertEqual( wf1._getStatusOf(dummy),
                          {'state': 'private', 'comments': ''} )
        self.assertEqual( wf2._getStatusOf(dummy),
                          {'state': 'confidential', 'comments': 'bar'} )
        
        # If we now publish it, the result should be the same as if we'd
        # publisehd first and then made
        
        wftool.doActionFor(dummy, 'publish', comment='foo' )
        self.assertEqual( wf1._getStatusOf(dummy),
                          {'state': 'published', 'comments': 'foo'} )
        self.assertEqual( wf2._getStatusOf(dummy),
                          {'state': 'confidential', 'comments': 'bar'} )
        
        self.assertEquals(['Manager', 'Owner'], sorted(rolesForPermissionOn('View', dummy)))
        
        # Now let's make it non-confidential. The result should be the same
        # as if it was published
        
        wftool.doActionFor(dummy, 'make_non_confidential', comment='baz' )
        self.assertEqual( wf1._getStatusOf(dummy),
                          {'state': 'published', 'comments': 'foo'} )
        self.assertEqual( wf2._getStatusOf(dummy),
                          {'state': 'nonconfidential', 'comments': 'baz'} )
        
        self.assertEquals(['Anonymous'], sorted(rolesForPermissionOn('View', dummy)))
    
def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)