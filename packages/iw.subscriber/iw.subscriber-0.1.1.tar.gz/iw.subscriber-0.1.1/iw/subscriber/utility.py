# -*- coding: utf-8 -*-
import datetime
import persistent
import zope.interface
import zope.component

from iw.subscriber import interfaces

class SubscriberUtility(persistent.Persistent):
    """local utility for iw.subscriber
    """
    zope.interface.implements(interfaces.ISubscriberUtility)

    def __init__(self):
        self._last_notification = None

    def setLast(self, value):
        if not isinstance(value, datetime.datetime):
            raise TypeError('last_notification must be a datetime')
        self._last_notification = value

    def getLast(self):
        if self._last_notification is None:
            return datetime.datetime.now() - self.interval
        return self._last_notification

    last_notification = property(getLast, setLast)

