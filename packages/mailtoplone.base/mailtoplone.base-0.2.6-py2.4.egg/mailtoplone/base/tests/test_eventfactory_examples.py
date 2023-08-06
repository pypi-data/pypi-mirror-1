# -*- coding: utf-8 -*-
#
# File: test_eventfactory_examples.py
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
import os

from zope import component

from mailtoplone.base.tests.base import MailToPloneBaseTestCase
from mailtoplone.base.interfaces import IEventFactory

DIRECTORY = os.path.dirname(__file__)

class TestEVTGoogle(MailToPloneBaseTestCase):

    def afterSetUp(self):
        icalstr = open(os.path.join(DIRECTORY, 'data/google.ics'),'rb').read()
        self.setRoles(('Manager',))
        factory = component.queryUtility(IEventFactory)
        factory.createEvent(icalstr, self.folder)
        self.e = self.folder.listFolderContents()[0]

    def testEventStartDate(self):
        self.failUnless(str(self.e.startDate.toZone('UTC')) == '2007/12/04 14:30:00 Universal')

    def testEventEndDate(self):
        self.failUnless(str(self.e.endDate.toZone('UTC')) == '2007/12/04 15:30:00 Universal')

class TestEVTOwa(MailToPloneBaseTestCase):

    def afterSetUp(self):
        icalstr = open(os.path.join(DIRECTORY, 'data/owa.ics'),'rb').read()
        self.setRoles(('Manager',))
        factory = component.queryUtility(IEventFactory)
        factory.createEvent(icalstr, self.folder)
        self.e = self.folder.listFolderContents()[0]

    def testEventStartDate(self):
        self.failUnless(str(self.e.startDate.toZone('UTC')) == '2008/02/12 08:00:00 Universal')

    def testEventEndDate(self):
        self.failUnless(str(self.e.endDate.toZone('UTC')) == '2008/02/12 09:00:00 Universal')

    def testEventAttendees(self):
        self.failUnless(self.e.attendees == (u'MisterXXX',))

class TestEVTPlone(MailToPloneBaseTestCase):

    def afterSetUp(self):
        icalstr = open(os.path.join(DIRECTORY, 'data/plone.ics'),'rb').read()
        self.setRoles(('Manager',))
        factory = component.queryUtility(IEventFactory)
        factory.createEvent(icalstr, self.folder)
        self.e = self.folder.listFolderContents()[0]
    
    def testEventStartDate(self):
        self.failUnless(str(self.e.startDate.toZone('UTC')) == '2008/01/11 08:25:00 Universal')

    def testEventEndDate(self):
        self.failUnless(str(self.e.endDate.toZone('UTC')) == '2008/01/11 09:25:00 Universal')

class TestEVTRfc2445(MailToPloneBaseTestCase):

    def afterSetUp(self):
        icalstr = open(os.path.join(DIRECTORY, 'data/rfc2445.ics'),'rb').read()
        self.setRoles(('Manager',))
        factory = component.queryUtility(IEventFactory)
        factory.createEvent(icalstr, self.folder)
        self.e = self.folder.listFolderContents()[0]
    
    def testEventStartDate(self):
        self.failUnless(str(self.e.startDate.toZone('UTC')) == '1998/03/12 13:30:00 Universal')

    def testEventEndDate(self):
        self.failUnless(str(self.e.endDate.toZone('UTC')) == '1998/03/12 14:30:00 Universal')

class TestEVTApple(MailToPloneBaseTestCase):

    def afterSetUp(self):
        icalstr = open(os.path.join(DIRECTORY, 'data/apple.ics'),'rb').read()
        self.setRoles(('Manager',))
        factory = component.queryUtility(IEventFactory)
        factory.createEvent(icalstr, self.folder)
        self.e = self.folder.listFolderContents()[0]
    
    def testEventStartDate(self):
        self.failUnless(str(self.e.startDate.toZone('UTC')) == '2008/02/13 17:15:00 Universal')

    def testEventEndDate(self):
        self.failUnless(str(self.e.endDate.toZone('UTC')) == '2008/02/13 18:15:00 Universal')

    def testEventAttendees(self):
        self.failUnless(self.e.attendees == (u'Mr. X', u'Mr. Y'))

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestEVTGoogle))
    suite.addTest(unittest.makeSuite(TestEVTOwa))
    suite.addTest(unittest.makeSuite(TestEVTPlone))
    suite.addTest(unittest.makeSuite(TestEVTRfc2445))
    suite.addTest(unittest.makeSuite(TestEVTApple))
    return suite

# vim: set ft=python ts=4 sw=4 expandtab :

