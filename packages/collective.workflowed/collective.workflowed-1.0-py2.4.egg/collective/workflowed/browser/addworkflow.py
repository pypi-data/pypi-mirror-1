from zope import schema
from zope.interface import Interface
from zope.component import adapts
from zope.interface import implements
from zope.formlib import form

from Acquisition import aq_inner

from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFCore.utils import getToolByName
from Products.Five.formlib import formbase
from Products.statusmessages.interfaces import IStatusMessage
from Products.CMFDefault.formlib.schema import SchemaAdapterBase

from plone.app.form.validators import null_validator
from plone.app.controlpanel.form import ControlPanelForm

from collective.workflowed import WorkflowedMessageFactory as _

class IAddWorkflowForm(Interface):
    """Define the fields for the new workflow
    """
    title=schema.TextLine(title=_(u"Title"),
                          description=_(u"This title will be shown in all workflow related control panels."),
                          required=True)
    description=schema.Text(title=_(u"Description"),
                            description=_(u"Free text, but some UI methods expect a bullet point list of characteristics in REST format."),
                            required=False)
    based_on=schema.Choice(title=_(u"Based on"),
                           description=_(u"Which workflow to use as a base. For empty workflows choose the single state workflow."),
                           missing_value=tuple(),
                           vocabulary="plone.app.vocabularies.Workflows",
                           required=True)

class AddWorkflowFormAdapter(SchemaAdapterBase):
    adapts(IPloneSiteRoot)
    implements(IAddWorkflowForm)
    title=''
    description=''
    based_on='one_state_workflow'

class AddWorkflowForm(ControlPanelForm):
    form_fields = form.FormFields(IAddWorkflowForm)
    form_name = _(u"Add workflow")
    label = _(u"Add workflow")
    description = _(u"Please enter the title and description for the new workflow and choose on which existing workflow it will be based.")
    
    def __call__(self):
        self.request.set('disable_border',True)
        return super(AddWorkflowForm,self).__call__()

    @form.action(_(u"Add"))
    def action_add(self, action, data):
        """Add a new workflow to the workflow tool
        """
        IStatusMessage(self.request).addStatusMessage(_(u"Workflow added."),type="info")
        context = aq_inner(self.context)
        wf_tool = getToolByName(context,'portal_workflow')
        plone_utils = getToolByName(self.context, 'plone_utils')
        workflow_id=plone_utils.normalizeString(data['title'])
        wf_tool.manage_pasteObjects(wf_tool.manage_copyObjects([data['based_on']]))
        wf_tool.manage_renameObject('copy_of_%s' % data['based_on'], workflow_id)
        wf_tool[workflow_id].setProperties(title=data['title'],description=data['description'])
        self.context.request.response.redirect('%s/@@workflowed-controlpanel?selected_workflow=%s' % (context.absolute_url(),workflow_id))
        return ''

    @form.action(_(u'label_cancel', default=u'Cancel'),
                 validator=null_validator,
                 name=u'cancel')
    def action_cancel(self, action, data):
        IStatusMessage(self.request).addStatusMessage(_("Add new workflow action canceled."),
                                                      type="info")
        self.request.response.redirect('%s/@@workflowed-controlpanel' % self.context.absolute_url())
        return ''

