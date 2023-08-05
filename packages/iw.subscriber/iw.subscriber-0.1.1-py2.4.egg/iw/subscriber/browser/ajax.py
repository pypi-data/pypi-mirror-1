# -*- coding: utf-8 -*-
import zope.component
from kss.core import KSSView
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IPloneSiteRoot
from iw.subscriber import interfaces
from iw.subscriber import utils

class ShowSubscribeLink(KSSView):

    def showSubscribeLink(self):
        referer = self.request.get('HTTP_REFERER', '')
        if not referer:
            return ''

        obj = utils.get_object_from_url(self.context, self.request, referer)

        core = self.getCommandSet('core')

        email = ''
        mtool = getToolByName(self.context,'portal_membership')
        if not mtool.isAnonymousUser():
            member = mtool.getAuthenticatedMember()
            email = member.getProperty('email')
        else:
            email = self.request.cookies.get('email','')

        data = interfaces.ISubscriberStorage(obj).get()
        if email and email in data:
            selector = 'unsubscribe'
        else:
            selector = 'subscribe'

        core.setStyle('#document-action-%s' % selector, 'display', 'inline')
        obj_url = obj.absolute_url()
        core.setAttribute('#document-action-%s a' % selector,
                          'href',
                          '%s/%s.html?email=%s' % (obj_url, selector, email))

        return self.render()



