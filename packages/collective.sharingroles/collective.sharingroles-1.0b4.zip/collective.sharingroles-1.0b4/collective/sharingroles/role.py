from persistent import Persistent
from zope.interface import implements
from plone.app.workflow.interfaces import ISharingPageRole

from zope.i18nmessageid import MessageFactory
PMF = MessageFactory('plone')

class PersistentSharingPageRole(Persistent):
    """These are registered as local utilities when managing the sharing
    page roles.
    """
    implements(ISharingPageRole)
    
    title = u""
    required_permission = None
    
    def __init__(self, title=u"", required_permission=None):
        self.title = PMF(title)
        self.required_permission = required_permission
