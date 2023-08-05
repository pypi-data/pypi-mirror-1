# -*- coding: utf-8 -*-
import datetime
import zope.interface
from zope.i18n import translate
from zope.app.schema.vocabulary import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm
from iw.subscriber import SubscriberMessageFactory as _

class IntervalsVocabulary(object):
    zope.interface.implements(IVocabularyFactory)
    vocabValues = [
                   (datetime.timedelta(1./96),
                    'now',
                    _('now', default='Now')),
                   (datetime.timedelta(1./24),
                    'hour',
                    _('hour', default='Each our')),
                   (datetime.timedelta(1),
                    'day',
                    _('day', default='Each day')),
                   (datetime.timedelta(7),
                    'week',
                    _('week', default='Each week')),
                  ]
    def __call__(self, context):
        vocab = [SimpleTerm(v, t, title=translate(l, context)) \
                     for v, t, l  in self.vocabValues]
        return SimpleVocabulary(vocab)

