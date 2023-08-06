from zope.interface import Interface
from zope import schema
from zope.i18nmessageid import MessageFactory
from zope.viewlet.interfaces import IViewlet

_ = MessageFactory('Products.PloneStatCounter')


class IStatCounterConfig(Interface):
    """Configuration for a StatCounter configlet.
    """

    sc_project   = schema.TextLine(title=_(u"Project id"), required=True)

    sc_invisible = schema.Bool(title=_(u"Invisible counter?"), default=True)

    sc_partition = schema.TextLine(title=_(u"Partition"), required=True)

    sc_security  = schema.TextLine(title=_(u"Security code"), required=True)


class IStatCounterViewlet(IViewlet):
    """
    """

    def renderJavascriptVariables(self):
        """Return rendered javascript variables for StatCounter.
        """
