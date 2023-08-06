# Zope imports
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.publisher.interfaces.browser import IBrowserView
from zope.viewlet.interfaces import IViewlet

# Plone imports
from plone.app.layout.viewlets.interfaces import IPortalFooter

# Local imports
from interfaces import IStatCounterConfig
from utility import StatCounterConfig
from utility import UTILITY_NAME
from viewlets import StatCounterViewlet


def importFinalSteps(context):
    """Install PloneStatCounter.
    """
    portal = context.getSite()
    addLocalUtility(portal)
    addViewlet(portal)

def addLocalUtility(portal):
    sm = portal.getSiteManager()
    if not sm.queryUtility(IStatCounterConfig, name=UTILITY_NAME):
        sm.registerUtility(StatCounterConfig(),
                           IStatCounterConfig,
                           UTILITY_NAME)

def addViewlet(portal):
    """Add the viewlet here (rather than in ZCML) so that it is only available
    when the local utility has been installed.
    """
    sm = portal.getSiteManager()
    sm.registerAdapter(StatCounterViewlet,
                       (Interface, IDefaultBrowserLayer, IBrowserView, IPortalFooter),
                       provided=IViewlet,
                       name='PloneStatCounter.statcounter'
                       )
