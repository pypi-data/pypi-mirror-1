from zope.i18nmessageid import MessageFactory

WorkflowedMessageFactory = MessageFactory('collective.workflowed')

def initialize(context):
    """Initializer called when used as a Zope 2 product."""
