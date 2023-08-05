# -*- coding: utf-8 -*-
#
# File: test_setup.py
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
from mailtoplone.base.interfaces import IInBox, IEmail, IMailDropBoxMarker, IMailDropBox
from mailtoplone.base.browser.xmlrpcview import IXMLRPCView
from Products.CMFCore.utils import getToolByName

class TestSetup(MailToPloneBaseTestCase):

    def afterSetUp(self):
        self.types = getToolByName(self.portal, 'portal_types')
        self.setRoles(('Manager',))
        self.portal.invokeFactory('InBox', 'inbox')
        self.portal.inbox.invokeFactory('Email', 'email')

    def test_mailtoplone_base_Email_installed(self):
        self.failUnless('Email' in self.types.objectIds())

    def test_mailtoplone_base_InBox_installed(self):
        self.failUnless('InBox' in self.types.objectIds())

    def test_IEmail_interface(self):
        self.failUnless(IEmail.providedBy(self.portal.inbox.email))

    def test_IInBox_interface(self):
        self.failUnless(IInBox.providedBy(self.portal.inbox))

    def test_IMailDropBoxMarker_interface(self):
        self.failUnless(IInBox.providedBy(self.portal.inbox))

    def test_Email_add_permisison(self):
        # The API of the permissionsOfRole() function sucks - it is bound too
        # closely up in the permission management screen's user interface
        self.failUnless('mailtoplone.base: Add Email' in [r['name'] for r in 
                                self.portal.permissionsOfRole('Manager') if r['selected']])
    def test_InBox_add_permisison(self):
        # The API of the permissionsOfRole() function sucks - it is bound too
        # closely up in the permission management screen's user interface
        self.failUnless('mailtoplone.base: Add InBox' in [r['name'] for r in 
                                self.portal.permissionsOfRole('Manager') if r['selected']])

    def test_Email_global_addable(self):
        result = True
        import sys
        try:
            self.portal.invokeFactory('Email','email2')
        except ValueError:
            if sys.exc_info()[1].__str__() == 'Disallowed subobject type: Email':
                result = False

        self.failUnless(result)

    def test_IMailDropBoxMarker_IMailDropBox_Adapter(self):
        self.failUnless(IMailDropBox(self.portal.inbox, None))

    def test_xmlrpcview_registered(self):
        self.portal.inbox.restrictedTraverse('xmlrpcview')
    
    def test_IXMLRPCView_interface(self):
        self.failUnless(IXMLRPCView.providedBy(self.portal.inbox.restrictedTraverse('xmlrpcview')))

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSetup))
    return suite

# vim: set ft=python ts=4 sw=4 expandtab :

