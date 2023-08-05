# -*- coding: utf-8 -*-
# Copyright (C)2007 Ingeniweb

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; see the file COPYING. If not, write to the
# Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""" defines a test class and its Plone Site layer for plone tests
"""
import zope.interface
from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite
import iw.email.testing

# setting up plone site
ptc.setupPloneSite(
    extension_profiles=[
        'iw.subscriber:default',
        ])

import iw.subscriber

class TestCase(ptc.FunctionalTestCase):
    """test case used in tests"""

    class layer(PloneSite):
        @classmethod
        def setUp(cls):
            fiveconfigure.debug_mode = True
            zcml.load_config('configure.zcml',
                             iw.subscriber)
            fiveconfigure.debug_mode = False
            iw.email.testing.smtpSetUp(None)

        @classmethod
        def tearDown(cls):
            iw.email.testing.smtpTearDown(None)

    def setUp(self):
        ptc.FunctionalTestCase.setUp(self)
        self.addMember('member1', roles=[])
        self.addMember('member2', email="", roles=[])

    def addMember(self, username, fullname="", email=None, roles=('Member',)):
        if 'Member' not in roles:
            roles = tuple(list(roles) + ['Member'])
        if email is None:
            email = '%s@example.com' % username
        if not fullname:
            fullname = '%s Dupont' % username.title()
        self.portal.portal_membership.addMember(username, 'secret', roles, [])
        member = self.portal.portal_membership.getMemberById(username)
        member.setMemberProperties({'fullname': fullname,
                                    'email': email,
                                    'firstname':'firstname',
                                    'lastname': 'lastname',
                                    })

