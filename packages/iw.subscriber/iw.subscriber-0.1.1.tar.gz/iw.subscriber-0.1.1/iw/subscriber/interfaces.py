# -*- coding: utf-8 -*-
import zope.interface

class ISubscriberUtility(zope.interface.Interface):
    """local utility for iw.subscriber
    """

class ISubscriberStorage(zope.interface.Interface):
    """adapter to get/set annotation storage
    """

    allow_subscription = zope.interface.Attribute(u"Allow Subscription")

    def get():
        """get data
        """


class IContentSubscriberData(zope.interface.Interface):
    """annotation to store subscription stuff
    """

    allow_subscription = zope.interface.Attribute(u"Allow Subscription")

    def add(value, name=''):
        """add an entry
        """

    def keys():
        """return subscribers emails
        """

    def items():
        """return subscribers mails and name
        """

    def __setitem__(key, value):
        """set a subscriber. value is a tuple (email, member)
        """

    def __delitem__(key):
        """delete a subscriber
        """

    def __contains__(key):
        """return True if key is in data
        """

class IMailer(zope.interface.Interface):
    """adapter to send email with the best available mailer
    """

    def send(sender, recipients, message):
        """send an email
        """

