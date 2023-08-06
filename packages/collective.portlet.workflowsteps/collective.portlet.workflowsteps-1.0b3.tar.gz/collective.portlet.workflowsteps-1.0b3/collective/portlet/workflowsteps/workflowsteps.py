import string

from zope.interface import implements
from zope.component import getMultiAdapter, getUtility

from zope.app.publisher.interfaces.browser import IBrowserMenu

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from zope import schema
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from collective.portlet.workflowsteps import WorkflowStepsMessageFactory as _

from plone.app.form.widgets.wysiwygwidget import WYSIWYGWidget

from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName

from plone.memoize.instance import memoize

class IWorkflowSteps(IPortletDataProvider):
    """A portlet which shows details of the current object's workflow. It
    will render the description of the current state as HTML, and optionally
    show available transitions.
    """

    header = schema.TextLine(title=_(u"Header"),
                             description=_(u"The portlet's header"))
    
    text = schema.Text(title=_(u"Text"),
                       description=_(u"Lead-in text shown before the current state description"),
                       required=False)
    
    show_state = schema.Bool(title=_(u"Show state"),
                             description=_(u"If selected, the description of the current "
                                            "workflow state of the object will be shown, "
                                            "with HTML tags allowed."),
                             required=True,
                             default=True)
    
    show_transitions = schema.Bool(title=_(u"Show transitions"),
                                   description=_(u"If selected, the available workflow transitions "
                                                  "will be shown, giving the user the ability to "
                                                  "invoke them."),
                                   required=True,
                                   default=True)
    
    show_transition_descriptions = schema.Bool(title=_(u"Show transition descriptions"),
                                   description=_(u"If selected, the description of each "
                                                  "transition will be shown, with HTML tags allowed."),
                                   required=True,
                                   default=True)

class Assignment(base.Assignment):
    """Portlet assignment.
    """

    implements(IWorkflowSteps)

    def __init__(self, header=u"", text=u"", show_state=True,
                    show_transitions=True, show_transition_descriptions=True):
        self.header = header
        self.text = text
        self.show_state = show_state
        self.show_transitions = show_transitions
        self.show_transition_descriptions = show_transition_descriptions

    @property
    def title(self):
        return self.header


class Renderer(base.Renderer):
    """Portlet renderer.
    """

    render = ViewPageTemplateFile('workflowsteps.pt')
    
    advanced = {} # is set by getting transition_info
    
    @property
    def available(self):
        return self.state_info or self.transition_info
    
    @property
    @memoize
    def review_state(self):
        return self.context_state.workflow_state()
    
    @property
    @memoize
    def state_info(self):
        
        if not self.data.show_state:
            return {}
        
        context = aq_inner(self.context)
        
        review_state = self.review_state
        portal_workflow = getToolByName(context, 'portal_workflow')
    
        workflows = portal_workflow.getWorkflowsFor(context)
        if workflows:
            for w in workflows:
                if w.states.has_key(self.review_state):
                    return {'id': review_state,
                            'title': w.states[review_state].title or review_state,
                            'description': self._interpolate(w.states[review_state].description)}
        
        return {}
    
    @property
    @memoize
    def transition_info(self):
        
        if not self.data.show_transitions:
            return []
        
        context = aq_inner(self.context)
        request = aq_inner(self.request)
        
        menu = getUtility(IBrowserMenu, name='plone_contentmenu_workflow')
    
        transition_info = []
        advanced = None
    
        for item in menu.getMenuItems(context, request):
            item_id = item.get('extra', {}).get('id', None)
            if item_id == 'advanced':
                self.advanced = item
            elif item_id == 'policy':
                continue
            else:
                item['description'] = self._interpolate(item['description'])
                transition_info.append(item)
        
        return transition_info
    
    @property
    @memoize
    def portal_state(self):
        return getMultiAdapter((self.context, self.request), name="plone_portal_state")

    @property
    @memoize
    def context_state(self):
        return getMultiAdapter((self.context, self.request), name="plone_context_state")
    
    def _interpolate(self, data):
        if not data:
            return ''
        template = string.Template(data)
        return template.safe_substitute(folder_url=self.context_state.folder().absolute_url(),
                                        object_url=self.context_state.object_url(),
                                        portal_url=self.portal_state.navigation_root_url())
    
class AddForm(base.AddForm):
    """Portlet add form.
    """
    form_fields = form.Fields(IWorkflowSteps)
    form_fields['text'].custom_widget = WYSIWYGWidget

    label = _(u"Add workflow steps portlet")
    description = _(u"A portlet which shows details about the current workflow state and next steps")

    def create(self, data):
        return Assignment(**data)

class EditForm(base.EditForm):
    """Portlet edit form.
    """
    form_fields = form.Fields(IWorkflowSteps)
    form_fields['text'].custom_widget = WYSIWYGWidget

    label = _(u"Edit workflow steps portlet")
    description = _(u"A portlet which shows details about the current workflow state and next steps")
