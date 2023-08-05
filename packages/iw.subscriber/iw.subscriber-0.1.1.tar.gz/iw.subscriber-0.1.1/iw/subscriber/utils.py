# -*- coding: utf-8 -*-
import zope.component
import base64
import urllib

def encode(email):
    """
    >>> from iw.subscriber import utils
    >>> print utils.encode('gael@ingeniweb.com')
    Z2FlbEBpbmdlbml3ZWIuY29t%0A


    """
    return urllib.quote(base64.encodestring(email))

def decode(encrypted):
    """
    >>> from iw.subscriber import utils
    >>> encrypted =  utils.encode('gael@ingeniweb.com')
    >>> print utils.decode(encrypted)
    gael@ingeniweb.com
    """
    return base64.decodestring(urllib.unquote(encrypted))

def is_folderish(context, request, check_url=False):
    state = zope.component.getMultiAdapter((context, request),
                                            name=u'plone_context_state')
    return state.is_folderish()

def get_object_from_url(context, request, url=''):
    state = zope.component.getMultiAdapter((context, request),
                                            name=u'plone_context_state')
    if state.is_folderish():
        return context

    if not url:
        url = request.ACTUAL_URL

    parent = context.aq_inner.aq_parent
    # this is the best way to see if we are on the default page
    if '/%s/%s' % (parent.getId(), context.getId()) in url:
        return context
    else:
        return parent



