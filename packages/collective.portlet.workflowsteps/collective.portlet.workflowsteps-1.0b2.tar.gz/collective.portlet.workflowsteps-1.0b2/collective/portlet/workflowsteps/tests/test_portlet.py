from zope.component import getUtility, getMultiAdapter

from plone.portlets.interfaces import IPortletType
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletRenderer

from plone.app.portlets.storage import PortletAssignmentMapping

from collective.portlet.workflowsteps import workflowsteps

from collective.portlet.workflowsteps.tests.base import TestCase


class TestPortlet(TestCase):

    def afterSetUp(self):
        self.setRoles(('Manager', ))

    def test_portlet_type_registered(self):
        portlet = getUtility(
            IPortletType,
            name='collective.portlet.workflowsteps.WorkflowSteps')
        self.assertEquals(portlet.addview,
                          'collective.portlet.workflowsteps.WorkflowSteps')

    def test_interfaces(self):
        portlet = workflowsteps.Assignment()
        self.failUnless(IPortletAssignment.providedBy(portlet))
        self.failUnless(IPortletDataProvider.providedBy(portlet.data))

    def test_invoke_add_view(self):
        portlet = getUtility(
            IPortletType,
            name='collective.portlet.workflowsteps.WorkflowSteps')
        mapping = self.portal.restrictedTraverse(
            '++contextportlets++plone.leftcolumn')
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse('+/' + portlet.addview)

        addview.createAndAdd(data={'header': u"Header",
                                   'text': u"Text",
                                   'show_state': False,
                                   'show_transitions': False,
                                   'show_transition_descriptions': False})

        self.assertEquals(len(mapping), 1)
        assignment = mapping.values()[0]
        self.failUnless(isinstance(assignment, workflowsteps.Assignment))
        
        self.assertEquals(u"Header", assignment.header)
        self.assertEquals(u"Text", assignment.text)
        self.assertEquals(False, assignment.show_state)
        self.assertEquals(False, assignment.show_transitions)
        self.assertEquals(False, assignment.show_transition_descriptions)

    def test_invoke_edit_view(self):
        mapping = PortletAssignmentMapping()
        request = self.folder.REQUEST

        mapping['foo'] = workflowsteps.Assignment()
        editview = getMultiAdapter((mapping['foo'], request), name='edit')
        self.failUnless(isinstance(editview, workflowsteps.EditForm))

    def test_obtain_renderer(self):
        context = self.folder
        request = self.folder.REQUEST
        view = self.folder.restrictedTraverse('@@plone')
        manager = getUtility(IPortletManager, name='plone.rightcolumn',
                             context=self.portal)

        assignment = workflowsteps.Assignment()

        renderer = getMultiAdapter(
            (context, request, view, manager, assignment), IPortletRenderer)
        self.failUnless(isinstance(renderer, workflowsteps.Renderer))


class TestRenderer(TestCase):

    def afterSetUp(self):
        self.folder.invokeFactory('Document', 'd1')

    def renderer(self, context=None, request=None, view=None, manager=None,
                 assignment=None, **kw):
        context = context or self.folder
        request = request or self.folder.REQUEST
        view = view or self.folder.restrictedTraverse('@@plone')
        manager = manager or getUtility(IPortletManager, name='plone.rightcolumn', context=self.portal)
        assignment = assignment or workflowsteps.Assignment(**kw)
        return getMultiAdapter((context, request, view, manager, assignment), IPortletRenderer).__of__(context)

    def test_render_call_no_error(self):
        r = self.renderer(context=self.folder.d1, assignment=workflowsteps.Assignment())
        r.update()
        output = r.render()
    
    def test_advanced_omitted_from_states(self):
        r = self.renderer(context=self.folder.d1, assignment=workflowsteps.Assignment())
        r.update()
        
        self.failUnless('workflow-transition-submit' in [a['extra']['id'] for a in r.transition_info])
        self.failIf('advanced' in [a['extra']['id'] for a in r.transition_info])
        self.failUnless(r.advanced)
        
    def test_state_description_interpolated(self):
        self.portal.portal_workflow['simple_publication_workflow'].states['private'].description = \
            "This is ${object_url} in ${folder_url} inside ${portal_url}."
        
        r = self.renderer(context=self.folder.d1, assignment=workflowsteps.Assignment())
        r.update()
        
        self.assertEquals("This is http://nohost/plone/Members/test_user_1_/d1 in http://nohost/plone/Members/test_user_1_ inside http://nohost/plone.",
                          r.state_info['description'])
    
    def test_transition_description_interpolated(self):
        self.portal.portal_workflow['simple_publication_workflow'].transitions['submit'].description = \
            "Do something to ${object_url} in ${folder_url} inside ${portal_url}."
        
        r = self.renderer(context=self.folder.d1, assignment=workflowsteps.Assignment())
        r.update()
        
        submitted = [s for s in r.transition_info if s['extra']['id'] == 'workflow-transition-submit'][0]
        
        self.assertEquals("Do something to http://nohost/plone/Members/test_user_1_/d1 in http://nohost/plone/Members/test_user_1_ inside http://nohost/plone.",
                          submitted['description'])

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPortlet))
    suite.addTest(makeSuite(TestRenderer))
    return suite
