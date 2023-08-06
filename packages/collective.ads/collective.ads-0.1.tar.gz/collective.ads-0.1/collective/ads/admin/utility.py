from zope.interface import Interface
from zope import schema
from zope.i18nmessageid import MessageFactory
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

_ = MessageFactory('portal_adsadmin')

class IAdsPortal(Interface):
    """This interface defines the Utility."""
    
class IAdsAdminControlPanelForm(Interface):
    """Control Panel Form"""
