# -*- coding: utf-8 -*-
import datetime
from zope.interface import Interface
from zope.component import getUtility
from zope.component import getSiteManager
from iw.subscriber.utility import SubscriberUtility
from iw.subscriber.interfaces import ISubscriberUtility
from iw.subscriber.browser.utility import IUtilitySchema

def setupVarious(context):
    """register a local utility
    """
    if context.readDataFile('iw.subscriber.various.txt') is None:
        return

    # add utility
    site = context.getSite()
    sm = getSiteManager(site)
    if sm.queryUtility(ISubscriberUtility) is None:
        utility = SubscriberUtility()
        sm.registerUtility(utility, ISubscriberUtility)

    # get utility
    adapted = IUtilitySchema(site)

    # set default values
    adapted.enable_subscriptions = True
    adapted.notify_created_only = False
    adapted.subscribed_types = ['Folder']
    vocab = getUtility(Interface,
                       name="plone.app.vocabularies.ReallyUserFriendlyTypes")
    adapted.notified_types = [t.token for t in vocab(site)]
    adapted.interval = datetime.timedelta(7)
    adapted.next_notification = datetime.datetime.now() + datetime.timedelta(7)


