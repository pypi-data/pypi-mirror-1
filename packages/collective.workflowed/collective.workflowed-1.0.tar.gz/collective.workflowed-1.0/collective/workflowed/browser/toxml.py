from zope.component import getUtility

from StringIO import StringIO
from Products.Five.browser import BrowserView

from collective.wtf.interfaces import ICSVWorkflowSerializer
from collective.wtf.exportimport import CSVWorkflowDefinitionConfigurator
        
class ToXML(BrowserView):
    """Export the context workflow to XML as a one-off
    """
    
    def __call__(self):
        
        wfdc = CSVWorkflowDefinitionConfigurator(self.context)
        xml = wfdc.__of__(self.context).generateWorkflowXML()

        self.request.response.setHeader("Content-type","text/xml")
        return xml
