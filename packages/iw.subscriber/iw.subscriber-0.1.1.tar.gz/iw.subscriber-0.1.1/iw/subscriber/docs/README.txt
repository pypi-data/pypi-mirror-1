=====================
iw.subscriber package
=====================
.. contents::

What is iw.subscriber ?
=======================

This package allow Plone users to subscribe to contents. Then they will be
notified on all creation/modification on this contents.

How to use iw.subscriber ?
==========================

You need a clock server. Add something like this to your zope.conf::

  <clock-server>
    # path_to_plone_site is the real path to your plone site
    method /path_to_plone_site/iw_subscriber_tick
    period 60
    user admin
    password xxx
    # You need your *real* virtual host here
    host www.example.com
  </clock-server>

If you use buildout, you just need to add this part in the zope-conf-additional
section of your plone.recipe.zope2instance.

