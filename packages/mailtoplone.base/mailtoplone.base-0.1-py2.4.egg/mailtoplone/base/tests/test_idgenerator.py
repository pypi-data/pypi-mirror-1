# -*- coding: utf-8 -*-
#
# File: test_eventfactory.py
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
from mailtoplone.base.interfaces import IIdGenerator


class TestIdGenerator(MailToPloneBaseTestCase):

    def afterSetUp(self):
        self.setRoles(('Manager',))
        self.idgen = component.queryUtility(IIdGenerator)
        self.testtype = 'Document'
        self.testid = 'myid'
    
    def testEmptyWithArg(self):
        self.failUnless(self.idgen.generateId(self.folder, self.testid) == self.testid)

    def testEmptyWithoutArg(self):
        self.failUnless(self.idgen.generateId(self.folder) == 'item')

    def testFullWithArg(self):
        self.folder.invokeFactory(self.testtype,self.testid)
        self.failUnless(self.idgen.generateId(self.folder, self.testid) == self.testid+"0")
        self.folder.invokeFactory(self.testtype,self.testid+"0")
        self.folder.invokeFactory(self.testtype,self.testid+"2")
        self.failUnless(self.idgen.generateId(self.folder, self.testid) == self.testid+"1")

    def testFullWithoutArg(self):
        self.folder.invokeFactory(self.testtype,'item')
        self.failUnless(self.idgen.generateId(self.folder) == 'item0')
        self.folder.invokeFactory(self.testtype,'item0')
        self.folder.invokeFactory(self.testtype,'item2')
        self.failUnless(self.idgen.generateId(self.folder) == 'item1')

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestIdGenerator))
    return suite

# vim: set ft=python ts=4 sw=4 expandtab :

