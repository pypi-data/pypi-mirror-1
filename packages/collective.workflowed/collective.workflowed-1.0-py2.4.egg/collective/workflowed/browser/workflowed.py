from plone.app.workflow.remap import remap_workflow
from plone.memoize.instance import memoize

from zope.component import getUtility
from zope.i18n import translate
from zope.schema.interfaces import IVocabularyFactory

from Acquisition import aq_inner

from Products.CMFCore.utils import getToolByName
from Products.CMFEditions.setuphandlers import DEFAULT_POLICIES
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone import PloneMessageFactory as pmf
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.app.controlpanel.form import ControlPanelView



class WorkflowedControlPanel(ControlPanelView):

    def __init__(self,context,request):
        super(WorkflowedControlPanel, self).__init__(context, request)
        request.set('disable_border', True)
        form = request.form
        submitted = form.get('form.submitted', False)
        save_button = form.get('form.button.Save', None) is not None
        cancel_button = form.get('form.button.Cancel', None) is not None
        if submitted and not cancel_button:
            request.response.redirect('%s/@@workflowed-controlpanel?selected_workflow=%s' % (context.absolute_url() , self.selected_workflow()))
        elif cancel_button:
            request.response.redirect(context.absolute_url() + '/plone_control_panel')

    @memoize
    def selected_workflow(self):
        context = aq_inner(self.context)
        form = self.request.form
        current_workflow=form.get('selected_workflow',self.available_workflows()[0]['id'])
        return current_workflow

    @memoize
    def available_workflows(self):
        vocab_factory = getUtility(IVocabularyFactory,
                                   name="plone.app.vocabularies.Workflows")
        workflows = []
        for v in vocab_factory(self.context):
            if v.title:
                title = translate(v.title, context=self.request)
            else:
                title = translate(v.token, domain='plone', context=self.request)
            workflows.append(dict(id=v.value, title=title) )
        def _key(v):
            return v['title']
        workflows.sort(key=_key)
        return workflows

    @memoize
    def current_workflow_url(self):
        context = aq_inner(self.context)
        portal_workflow = getToolByName(context, 'portal_workflow')
        wf = getattr(portal_workflow, self.selected_workflow())
        return wf.absolute_url()

    @memoize
    def current_workflow_data(self):
        context = aq_inner(self.context)
        portal_workflow = getToolByName(context, 'portal_workflow')
        wf = getattr(portal_workflow, self.selected_workflow())
        text = translate(wf.description.strip(), domain='plone', context=self.request)
        return dict(title=wf.title,description=[s.strip() for s in text.split('- ') if s],initial_state=wf.states.initial_state,transitions=wf.transitions.objectValues(),states=wf.states.objectValues())

    def generate_workflow_js(self):
        wf=self.current_workflow_data()
        javascript= """var workflow=new Workflow('workflow_editor');
        var w = new GUIPalette();
        workflow.setToolWindow(w);
        w.setPosition(20,20);
        var dialog = new VectorPropertyWindow();
        workflow.addFigure(dialog,700,20);
        """
        state_template="""
          var figure = new StateWindow("%s");
          figure.setDimension(160,40);
          figure_outputPort = new OutputPort();
          figure_outputPort.setDirection(-1);
          figure_outputPort.setMaxFanOut(1000);
          figure_outputPort.setWorkflow(workflow);
          figure_outputPort.setBackgroundColor(new Color(245,115,115));
          figure_inputPort = new InputPort();
          figure_inputPort.setDirection(-1);
          figure_inputPort.setWorkflow(workflow);
          figure_inputPort.setBackgroundColor(new Color(115,245,115));
          figure_inputPort.setColor(null);
          figure.addPort(figure_outputPort,160,25);
          figure.addPort(figure_inputPort,160,40);
          workflow.addFigure(figure,%d,%d);
        """
        x=150
        y=20
        for state in wf['states']:
            new_state=state_template % (state.id,x,y)
            javascript=javascript + new_state.replace('figure','st_%s' % state.id)
            if wf['initial_state']==state.id:
                javascript=javascript+"st_%s.setLineWidth(3)\n" % state.id
            y=y+120
        transition_template="""
          var figure = new TransitionWindow("%s");
          figure.setDimension(120,40);
          figure_outputPort = new OutputPort();
          figure_outputPort.setDirection(-1); 
          figure_outputPort.setMaxFanOut(1); 
          figure_outputPort.setWorkflow(workflow);
          figure_outputPort.setBackgroundColor(new Color(115,245,115));
          figure_inputPort = new InputPort();
          figure_inputPort.setDirection(-1);
          figure_inputPort.setWorkflow(workflow);
          figure_inputPort.setBackgroundColor(new Color(245,115,111));
          figure_inputPort.setColor(null);
          figure.addPort(figure_outputPort,0,25);
          figure.addPort(figure_inputPort,0,40);
          workflow.addFigure(figure,%d,%d);
        """
        x=500
        y=20
        for transition in wf['transitions']:
            new_transition=transition_template % (transition.id,x,y)
            javascript=javascript + new_transition.replace('figure','tr_%s' % transition.id)
            y=y+90
        for state in wf['states']:
            for transition in state.transitions:
                javascript=javascript+"""
          if (typeof(tr_%s_inputPort)!="undefined") {
            var connection = new Connection();
            connection.setSource(st_%s_outputPort);
            connection.setTarget(tr_%s_inputPort);
            workflow.addFigure(connection);
          }
        """ % (transition,state.id,transition)
        for transition in wf['transitions']:
                javascript=javascript+"""
          if (typeof(st_%s_inputPort)!="undefined") {
            var connection = new Connection();
            connection.setSource(tr_%s_outputPort);
            connection.setTarget(st_%s_inputPort);
            workflow.addFigure(connection);
          }
        """ % (transition.new_state_id,transition.id,transition.new_state_id)
        return javascript
