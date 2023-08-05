# -*- coding: utf-8 -*-
## Copyright (C) 2007 Ingeniweb - all rights reserved
## No publication or distribution without authorization.

from Products.CMFPlone.CatalogTool import registerIndexableAttribute
from iw.subscriber.interfaces import ISubscriberStorage


def getMails(object, portal, **kw):
    data = ISubscriberStorage(object).get()
    return data.keys()

registerIndexableAttribute('getMails', getMails)


def canSubscribe(object, portal, **kw):
    data = ISubscriberStorage(object).get()
    return data.allow_subscription and 1 or 0

registerIndexableAttribute('canSubscribe', canSubscribe)

def isSubscribed(object, portal, **kw):
    data = ISubscriberStorage(object).get()
    if len(data.keys()) > 0:
        return 1
    return 0

registerIndexableAttribute('isSubscribed', isSubscribed)

INDEXES = ['getMails', 'canSubscribe', 'isSubscribed']
