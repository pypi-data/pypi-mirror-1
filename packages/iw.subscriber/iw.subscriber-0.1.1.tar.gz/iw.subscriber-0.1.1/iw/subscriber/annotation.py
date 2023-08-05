# -*- coding: utf-8 -*-
import zope.interface
import zope.component
import persistent
from persistent.dict import PersistentDict

from iw.subscriber import interfaces

class ContentSubscriberData(persistent.Persistent):
    """Annotation to store subscription stuff::

        >>> from iw.subscriber.annotation import ContentSubscriberData

    Check implementation::

        >>> from iw.subscriber.interfaces import IContentSubscriberData
        >>> from zope.interface import verify
        >>> verify.verifyClass(IContentSubscriberData, ContentSubscriberData)
        True


    Let's try to add an email::

        >>> data = ContentSubscriberData()
        >>> data.add('gael@example.com')

        >>> 'gael@example.com' in data
        True

        >>> data.keys()
        ['gael@example.com']

    Then remove it::

        >>> del data['gael@example.com']

        >>> data.keys()
        []

    """

    zope.interface.implements(interfaces.IContentSubscriberData)

    def __init__(self):
        self.data = PersistentDict()
        self.allow_subscription = True

    def add(self, value, name=''):
        self.data[value] = name

    def keys(self):
        return self.data.keys()

    def items(self):
        return self.data.items()

    def __setitem__(self, key, value):
        self.data[key] = value

    def __delitem__(self, key):
        del self.data[key]

    def __contains__(self, key):
        return key in self.data

    def __repr__(self):
        return '<ContentSubscriberData with %i subscriber(s))>' % (
                        len(self.data.keys()),)

    def manage_fixupOwnershipAfterAdd(self):
        """needed because CMFPlone/patches/interfacePatch.py make is horrible
        patch
        """
