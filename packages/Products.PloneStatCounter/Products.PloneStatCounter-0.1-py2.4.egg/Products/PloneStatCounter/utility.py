from zope.interface import implements
from zope.schema.fieldproperty import FieldProperty

from interfaces import IStatCounterConfig

from OFS.SimpleItem import SimpleItem

UTILITY_NAME = 'statcounter_config'

class StatCounterConfig(SimpleItem):
    """A local utility that stores StatCounter configuration.
    """

    implements(IStatCounterConfig)

    sc_project   = FieldProperty(IStatCounterConfig['sc_project'])
    sc_invisible = FieldProperty(IStatCounterConfig['sc_invisible'])
    sc_partition = FieldProperty(IStatCounterConfig['sc_partition'])
    sc_security  = FieldProperty(IStatCounterConfig['sc_security'])
