# -*- coding: utf-8 -*-
import zope.component
import zope.interface
from Products.Five import BrowserView
from Products.CMFPlone.interfaces import IPloneSiteRoot
from iw.subscriber.browser.subscribe import BaseForm
from iw.subscriber import interfaces
from iw.subscriber import utils

def check_parents(context, email):
    obj = context
    while not IPloneSiteRoot.providedBy(obj):
        data = interfaces.ISubscriberStorage(obj).get()
        if email in data:
            return False
        obj = obj.aq_parent
    return True

class Actions(BaseForm):

    def show(self):
        obj = utils.get_object_from_url(self.context, self.request)

        sm = zope.component.getSiteManager(self.context)
        utility = sm.getUtility(interfaces.ISubscriberUtility)

        if IPloneSiteRoot.providedBy(obj):
            # FIXME later
            return False

        if obj.portal_type in utility.subscribed_types:
            email, name = self._infos()
            return check_parents(obj.aq_inner, email)

        return False



