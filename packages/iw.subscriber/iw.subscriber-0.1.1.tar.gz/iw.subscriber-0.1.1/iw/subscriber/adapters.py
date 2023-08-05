# -*- coding: utf-8 -*-
import zope.interface
import zope.component
from persistent.dict import PersistentDict
from zope.annotation.interfaces import IAnnotations
from zope.sendmail.interfaces import IMailDelivery
from Products.Archetypes.atapi import BaseObject
from Products.CMFPlone.Portal import PloneSite
from Products.CMFCore.utils import getToolByName
from iw.subscriber.annotation import ContentSubscriberData
from iw.subscriber import interfaces
from iw.subscriber import config

class SubscriberStorage(object):

    def __init__(self, context):
        self.context = context.aq_inner

    def _setAllowSubscription(self, value=True):
        data = self.get()
        if not value:
            data.__init__()
        data.allow_subscription = value

    def _getAllowSubscription(self):
        data = self.get()
        return data.allow_subscription

    allow_subscription = property(_getAllowSubscription, _setAllowSubscription)

    def get(self):
        annotations = IAnnotations(self.context)
        if config.ANNOTATION_KEY not in annotations.keys():
            data = ContentSubscriberData()
            annotations[config.ANNOTATION_KEY] = data
        return annotations.get(config.ANNOTATION_KEY)

class ContentSubscriberStorage(SubscriberStorage):
    zope.interface.implements(interfaces.ISubscriberStorage)
    zope.component.adapts(BaseObject)

class SiteSubscriberStorage(SubscriberStorage):
    zope.interface.implements(interfaces.ISubscriberStorage)
    zope.component.adapts(PloneSite)


class Mailer(object):

    zope.interface.implements(interfaces.IMailer)
    zope.component.adapts(PloneSite)

    def __init__(self, context):
        self.context = context
        self.mailer = zope.component.queryUtility(IMailDelivery,
                                                'iw.subscriber.mailer')
        if self.mailer is None:
            self.accept_list = False
            self.mailer = getToolByName(self.context,'MailHost')
        else:
            self.accept_list = True

    def send(self, sender, recipient, message):
        if self.accept_list:
            recipient = [recipient]
        self.mailer.send(sender, recipient, message)

