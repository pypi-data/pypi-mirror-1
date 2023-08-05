# -*- coding: utf-8 -*-
import datetime
import zope.schema
import zope.component
import zope.interface
from zope.formlib import form
from plone.app.controlpanel.form import ControlPanelForm
from plone.app.controlpanel import widgets
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone.Portal import PloneSite
from p4a.datetimewidgets.widgets import DatetimeWidget

from iw.subscriber import interfaces
from iw.subscriber import SubscriberMessageFactory as _

class IUtilitySchema(zope.interface.Interface):

    enable_subscriptions = zope.schema.Bool(title=_('enable_subscriptions', default='Enable subscriptions'),
                                            default=True)
    subscribed_types = zope.schema.Tuple(title=_('subscribed_types', default='Subscribed types'),
                                      value_type=zope.schema.Choice(
                                          vocabulary="plone.app.vocabularies.ReallyUserFriendlyTypes"))
    notified_types = zope.schema.Tuple(title=_('notified_types', default='Notified types'),
                                      value_type=zope.schema.Choice(
                                          vocabulary="plone.app.vocabularies.ReallyUserFriendlyTypes"))
    notify_created_only = zope.schema.Bool(title=_('notify_created_only', default='Notify created only'))
    interval = zope.schema.Choice(title=_('interval', default='Interval'),
                                  vocabulary="iw.subscriber.vocabularies.Intervals",
                                  constraint=lambda v: isinstance(v, datetime.timedelta))
    next_notification = zope.schema.Datetime(title=_('next_notification', default='Next notification'))

class UtilityProperty(object):

    def __init__(self, name, default=None):
        self.__name__ = name
        self.default = default

    def __get__(self, instance, owner):
        sm = zope.component.getSiteManager(instance.context)
        utility = sm.getUtility(interfaces.ISubscriberUtility)
        return getattr(utility, self.__name__, self.default)


    def __set__(self, instance, value):
        sm = zope.component.getSiteManager(instance.context)
        utility = sm.getUtility(interfaces.ISubscriberUtility)
        return setattr(utility, self.__name__, value)

class DatetimeProperty(UtilityProperty):

    def __get__(self, instance, owner):
        sm = zope.component.getSiteManager(instance.context)
        utility = sm.getUtility(interfaces.ISubscriberUtility)
        try:
            return datetime.datetime.now() + utility.interval
        except TypeError:
            return datetime.datetime.now()

class UtilitySchemaAdapter(SchemaAdapterBase):
    zope.interface.implements(IUtilitySchema)
    zope.component.adapts(PloneSite)

    enable_subscriptions = UtilityProperty('enable_subscriptions', True)
    subscribed_types = UtilityProperty('subscribed_types', default=['Folder'])
    notified_types = UtilityProperty('notified_types', default=[])
    notify_created_only = UtilityProperty('notify_created_only', False)
    interval = UtilityProperty('interval', datetime.timedelta(7))
    next_notification = DatetimeProperty('next_notification',
                                         datetime.datetime.now()+datetime.timedelta(7))

class UtilityForm(ControlPanelForm):
    label = _('label_subscription_settings',
              default='Subscription settings')
    description=None
    form_name = _('label_subscription_settings',
                  default='Subscription settings')

    form_fields = form.FormFields(IUtilitySchema)
    form_fields['subscribed_types'].custom_widget = widgets.MultiCheckBoxThreeColumnWidget
    form_fields['notified_types'].custom_widget = widgets.MultiCheckBoxThreeColumnWidget
    form_fields['next_notification'].custom_widget = DatetimeWidget

