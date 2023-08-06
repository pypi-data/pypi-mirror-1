# -*- coding: utf-8 -*-
#
# File: test_emailview.py
#
# Copyright (c) InQuant GmbH
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

__author__    = """Hans-Peter Locher <hans-peter.locher@inquant.de>"""
__docformat__ = 'plaintext'

import unittest
from zope import component

from mailtoplone.base.tests.base import MailToPloneBaseTestCase
from mailtoplone.base.interfaces import IEmail
from mailtoplone.base.browser.emailview import IEmailView

class TestEmailViewSetup(MailToPloneBaseTestCase):

    def afterSetUp(self):
        self.setRoles(('Manager',))
        self.portal.invokeFactory('Email', 'm1')

    def test_emailview_registered(self):
        self.portal.m1.restrictedTraverse('view')

    def test_IEmailView_interface(self):
        self.failUnless(IEmailView.providedBy(self.portal.m1.restrictedTraverse('view')))

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestEmailViewSetup))
    return suite

# vim: set ft=python ts=4 sw=4 expandtab :

