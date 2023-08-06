from zope.i18nmessageid import MessageFactory
from zope.interface import Interface


MultiTemplateMessageFactory = MessageFactory('collective.multitemplate')


class IMultiTemplate(Interface):
    """An interface to register multiple templates on the same object
       distinguished by name
    """
