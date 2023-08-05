# -*- coding: utf-8 -*-
import zope.event
import zope.schema
import zope.component
import zope.interface
import zope.lifecycleevent
from zope.formlib import form
from zope.app.form.browser import TextWidget
from plone.app.form.base import EditForm
from plone.app.form.validators import null_validator
from plone.app.form.events import EditBegunEvent, EditCancelledEvent, EditSavedEvent
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.Archetypes.atapi import BaseObject
from Products.CMFPlone.Portal import PloneSite
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFPlone import PloneMessageFactory as _p

from iw.subscriber import interfaces
from iw.subscriber import utils
from iw.subscriber.catalog import INDEXES
from iw.subscriber import SubscriberMessageFactory as _

class SubscriberInfos(object):

    def _infos(self):
        mtool = getToolByName(self.context,'portal_membership')
        if mtool.isAnonymousUser():
            try:
                email = self.request.form.get('email')
            except AttributeError:
                email = ''
            name = ''
        else:
            member = mtool.getAuthenticatedMember()
            email = member.getProperty('email')
            name = str(member)
        return email, name


class BaseForm(BrowserView, SubscriberInfos):

    def nextURL(self, message='', level='info', view=''):
        if message:
            utool = getToolByName(self.context,'plone_utils')
            utool.addPortalMessage(message, level)
        url = zope.component.getMultiAdapter((self.context, self.request),
                                              name='absolute_url')
        return self.request.response.redirect(url()+'/'+view)


class SubscribeView(BaseForm):

    def __call__(self):
        email, name = self._infos()
        if not email or not name:
            if email:
                self.request.form['form.email'] = email
            view = zope.component.getMultiAdapter((self.context, self.request),
                                                  name='subscribe_form.html')
            output = view()
            email = self.request.form.get('form.email')
            if email:
                self.request.response.setCookie('email', email)
            return output
        else:
            data = interfaces.ISubscriberStorage(self.context).get()
            data.add(email, name)
            self.context.reindexObject(idxs=INDEXES)
            level = 'info'
            message = _('subscription_ok',
                        default=u"You just subscribe to this content")
        return self.nextURL(message=message, level=level)

class UnsubscribeView(BaseForm):

    def __call__(self):
        data = interfaces.ISubscriberStorage(self.context).get()
        email, name = self._infos()
        if email in data:
            del data[email]
        self.context.reindexObject(idxs=INDEXES)
        level = 'info'
        message = _('unsubscription_ok',
                    default=u"You just unsubscribe from this content")
        return self.nextURL(message=message, level=level)

class IEmailSchema(zope.interface.Interface):

    email = zope.schema.TextLine(
            title=_('your_email', default=u'Your email'))

class EmailSchemaAdapter(SchemaAdapterBase, SubscriberInfos):
    zope.interface.implements(IEmailSchema)

    def getEmail(self):
        email, name = self._infos()
        return email

    def setEmail(self, value):
        mtool = getToolByName(self.context,'portal_membership')
        if not mtool.isAnonymousUser():
            member = mtool.getAuthenticatedMember()
            if not member.getProperty('email'):
                member.setMemberProperties(
                        dict(email=value.encode('utf-8')))
        email, name = self._infos()
        data = interfaces.ISubscriberStorage(self.context).get()
        data.add(value, name)
        self.context.reindexObject(idxs=INDEXES)

    email = property(getEmail, setEmail)

class SubscribeForm(EditForm, BaseForm):

    @property
    def label(self):
        return _('subscribe_form_label', default='Subscribe ${title}',
                    mapping=dict(title=self.context.Title()))

    @property
    def description(self):
        if utils.is_folderish(self.context, self.request):
            return _('subscribe_form_description', default='''Please enter your
                     email to subscribe this content. You will receive a
                     confirmation email and you can unsubscribe by following
                     the link in this email''')
        else:
            return _('subscribe_folder_form_description', default='''Please
                     enter your email to subscribe to all content in this
                     folder. You will receive a confirmation email and you can
                     unsubscribe by following the link in this email.  ''')

    form_name = label
    form_fields = form.FormFields(IEmailSchema)

    @form.action(_(u"Subscribe", default="Subscribe"),
                 condition=form.haveInputWidgets,
                 name=u'save')
    def handle_save_action(self, action, data):
        if form.applyChanges(self.context, self.form_fields,
                             data, self.adapters):
            zope.event.notify(
                    zope.lifecycleevent.ObjectModifiedEvent(self.context))
            zope.event.notify(EditSavedEvent(self.context))
            self.status = "Changes saved"
        else:
            zope.event.notify(EditCancelledEvent(self.context))
            self.status = "No changes"
        url = zope.component.getMultiAdapter((self.context, self.request),
                                              name='absolute_url')()
        level = 'info'
        message = _('subscription_ok',
                    default=u"You just subscribe to this content")
        return self.nextURL(message=message, level=level)

    @form.action(_p(u"label_cancel", default=u"Cancel"),
                 validator=null_validator,
                 name=u'cancel')
    def handle_cancel_action(self, action, data):
        zope.event.notify(EditCancelledEvent(self.context))
        self.nextURL()

class IHiddenEmailSchema(zope.interface.Interface):

    email = zope.schema.TextLine(
            title=_('your_email', default=u'Your email'),
                    required=False)

class UnsubscribeSchemaAdapter(EmailSchemaAdapter):
    zope.interface.implements(IHiddenEmailSchema)

    def setEmail(self, value):
        data = interfaces.ISubscriberStorage(self.context).get()
        if value in data:
            del data[value]
            self.context.reindexObject(idxs=INDEXES)

    email = property(EmailSchemaAdapter.getEmail, setEmail)

class HiddenWidget(TextWidget):
    label = u''
    def __call__(self):
        return self.hidden()


class UnsubscribeForm(EditForm, BaseForm):

    label = _('unsubscribe_form_label', default='Subscription preferences')

    @property
    def description(self):
        return _('unsubscribe_form_description', default='''You subscribed the
                  notifications with the following email address : ${email}''',
                  mapping=dict(email=self.request.get('email','')))

    form_name = label
    form_fields = form.FormFields(IHiddenEmailSchema)
    form_fields['email'].custom_widget = HiddenWidget

    @form.action(_(u"Unsubscribe", default="Unsubscribe"),
                 condition=form.haveInputWidgets,
                 name=u'save')
    def handle_save_action(self, action, data):
        if form.applyChanges(self.context, self.form_fields,
                             data, self.adapters):
            zope.event.notify(
                    zope.lifecycleevent.ObjectModifiedEvent(self.context))
            zope.event.notify(EditSavedEvent(self.context))
            self.status = "Changes saved"
        else:
            zope.event.notify(EditCancelledEvent(self.context))
            self.status = "No changes"
        url = zope.component.getMultiAdapter((self.context, self.request),
                                              name='absolute_url')()
        level = 'info'
        message = _('unsubscription_ok',
                    default=u"You just unsubscribe to this content")
        return self.nextURL(message=message, level=level)

    @form.action(_p(u"label_cancel", default=u"Cancel"),
                 validator=null_validator,
                 name=u'cancel')
    def handle_cancel_action(self, action, data):
        zope.event.notify(EditCancelledEvent(self.context))
        self.nextURL()

    def __call__(self):
        email = self.request.get('v',None)
        if email is not None:
            email = utils.decode(email)
        else:
            email, name = self._infos()
        if email:
            self.request.form['form.email'] = email
            self.request.form['email'] = email
        return super(UnsubscribeForm, self).__call__()
