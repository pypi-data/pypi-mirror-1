# -*- coding: utf-8 -*-
import datetime
import zope.component
from DateTime import DateTime
from BTrees.OOBTree import OOBTree, OOSet, intersection
from BTrees.OIBTree import OIBTree
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from iw.subscriber import interfaces
from iw.subscriber import utils
from iw.subscriber import LOG
from iw.email import MultipartMail

class NotificationsData(object):
    """An object to store notifications from brains::

        >>> from iw.subscriber.browser.tick import NotificationsData

        >>> brain = TestBrain('/plone/brain1', ['gael@ingeniweb.com'])
        >>> brains = [TestBrain('/plone/brain1/sub%i' %i) for i in xrange(20)]
        >>> len(brains)
        20

        >>> notifications = NotificationsData()
        >>> notifications.addBrains(brain, brains)

        >>> [k for k in notifications.keys()]
        ['gael@ingeniweb.com']

        >>> values = notifications.get('gael@ingeniweb.com')
        >>> len([v for v in values.values()[0]])
        20
    """

    def __init__(self):
        self.paths = OOBTree()
        self.brains = OOBTree()
        self.emails = OOBTree()

    def keys(self):
        return self.emails.keys()

    def get(self, key):
        paths = self.emails.get(key, [])
        containers = {}
        for path in paths:
            brains = OOBTree()
            btree = self.paths.get(path, OOBTree())
            for npath in btree.keys():
                if npath != path:
                    brains[npath] = self.brains[npath]
            containers[self.brains[path]] = brains.values()
        return containers

    def addBrains(self, brain, values):
        if not values:
            return

        path = brain.getPath()
        self.brains[path] = brain

        paths = self.paths.get(path, OOBTree())
        for b in values:
            p = b.getPath()
            self.brains[p] = b
            paths[p] = 1
        self.paths[path] = paths

        emails = brain.getMails
        for email in emails:
            values = self.emails.get(email, OIBTree())
            values[path] = 1
            self.emails[email] = values

class Tick(BrowserView):

    def __init__(self, context, request):
        self.context = context
        self.request = request
        sm = zope.component.getSiteManager(self.context)
        self.util = sm.getUtility(interfaces.ISubscriberUtility)
        self.now = datetime.datetime.now()

    def getContents(self):
        ctool = getToolByName(self.context,'portal_catalog')

        types = set(self.util.subscribed_types)|set(self.util.notified_types)
        types = [t for t in types]

        if not types:
            return []

        last_notification = DateTime(
                self.util.last_notification.strftime('%x %X'))
        now = DateTime(self.now.strftime('%x %X'))
        query = dict(query=(last_notification, now),
                     range='minmax')

        brains = ctool(portal_type=self.util.subscribed_types,
                       isSubscribed=True,
                       Language='all')


        def getSubContents(path, lang):
            _lang = lang or 'all'
            _brains = [_b for _b in ctool(portal_type=types,
                                        Language=_lang,
                                        path=path,
                                        created=query)]
            if not self.util.notify_created_only:
                _brains = [_b for _b in ctool(portal_type=types,
                                            Language=_lang,
                                            path=path,
                                            modified=query)]
            return _brains

        paths = []
        contents = NotificationsData()
        for b in brains:
            path = b.getPath()
            lang = b.Language
            LOG.info('Get content to notify for %s', path)
            LOG.info('%s, %s > %s', b.modified > last_notification,
                     b.modified, last_notification)
            if path not in paths:
                if b.is_folderish:
                    LOG.info('Add %s contents to notify list', path)
                    contents.addBrains(b, getSubContents(path, lang))
                    #if '/plone/level1_folder2' in path:
                    #    import pdb; pdb.set_trace()
                elif b.modified > last_notification:
                    LOG.info('Added %s to notify list', path)
                    contents.addBrains(b, [b])
                paths.append(path)

        #import pdb; pdb.set_trace()

        return contents

    def notify(self, contents):
        mailer = interfaces.IMailer(self.context)
        LOG.info('Start notify contents with %s mailer.',
                 mailer.mailer.__class__.__name__)

        subject = zope.component.getMultiAdapter((self.context, self.request),
                                                  name='iw.subscriber.subject')
        body = zope.component.getMultiAdapter((self.context, self.request),
                                                  name='iw.subscriber.body')

        portal = getToolByName(self.context,'portal_url').getPortalObject()
        mfrom = portal.email_from_adress

        for email in contents.keys():
            brains = contents.get(email)
            if not brains:
                continue
            msubject = subject.index(mfrom=mfrom, email=email, brains=brains)
            msubject = msubject.strip()
            mbody = body.index(mfrom=mfrom,
                               email=email, crypted=utils.encode(email),
                               brains=brains)
            mail = MultipartMail(html=mbody,
                                 mfrom=mfrom, mto=email,
                                 subject=msubject.strip())
            mailer.send(mfrom, email, str(mail))

    def force(self):
        now = datetime.datetime.now()
        self.util.next_notification = now
        self.util.last_notification = now - datetime.timedelta(15)
        return self.__call__(now=now)

    def __call__(self, now=None):
        LOG.debug('tick start')

        if not self.util.enable_subscriptions:
            return 'DISABLED'

        if now is None:
            now = datetime.datetime.now()

        strfnow = now.strftime('%x %H:%M')

        if self.util.next_notification.strftime('%x %H:%M') != strfnow:
            LOG.info("Don't notify. Stoping")
            return 'DONT NOTIFY %s %s' % (self.util.next_notification,
                                          strfnow)

        contents = self.getContents()

        if not len(contents.keys()):
            LOG.info('No contents to notify. Stoping')
            return 'NOTHING TO DO'
        else:
            self.notify(contents)
            self.util.last_notification = self.now
            self.util.next_notification = self.now + self.util.interval

        LOG.debug('tick ended')
        return '%s OK' % len(contents.keys())

