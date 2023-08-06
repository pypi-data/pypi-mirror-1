from zope.component import getUtility

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase

from interfaces import IStatCounterConfig
from utility import UTILITY_NAME


VARIABLE_TEMPLATE = """
    sc_project=%(sc_project)s;
    sc_invisible=%(sc_invisible)s;
    sc_partition=%(sc_partition)s;
    sc_security="%(sc_security)s";
"""


class StatCounterViewlet(ViewletBase):
    """A viewlet that renders a snippet of XHTML providing a StatCounter page
    counter on a page.
    """

    render = ViewPageTemplateFile('statcounter.pt')

    def update(self):
        # set here the values that you need to grab from the template.
        # stupid example:
        config = getUtility(IStatCounterConfig, name=UTILITY_NAME)
        self.sc_project = config.sc_project
        # Convert a boolean (True/False) into a 1 or 0.
        self.sc_invisible = config.sc_invisible and 1 or 0
        self.sc_partition = config.sc_partition
        self.sc_security = config.sc_security

    def renderJavascriptVariables(self):
        """Return rendered javascript variables for StatCounter.
        """
        return VARIABLE_TEMPLATE % self.__dict__
