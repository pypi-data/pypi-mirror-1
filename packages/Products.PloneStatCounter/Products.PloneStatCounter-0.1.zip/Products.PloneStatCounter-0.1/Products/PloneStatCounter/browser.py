from zope.component import getUtility
from zope.formlib import form
from zope.i18nmessageid import MessageFactory

from Products.Five.formlib import formbase

from interfaces import IStatCounterConfig

_ = MessageFactory('Products.PloneStatCounter')


class StatCounterConfigForm(formbase.EditFormBase):
    form_fields = form.Fields(IStatCounterConfig)

    label = _(u"StatCounter configuration form")


def form_adapter(context):
    return getUtility(IStatCounterConfig,
                      name='statcounter_config',
                      context=context)
