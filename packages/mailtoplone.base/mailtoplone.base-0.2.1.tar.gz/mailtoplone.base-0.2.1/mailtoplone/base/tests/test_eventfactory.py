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
from zope.component import adapter

from Products.Archetypes.interfaces import IObjectInitializedEvent

from mailtoplone.base.tests.base import MailToPloneBaseTestCase
from mailtoplone.base.interfaces import IEventFactory

ICALSTR="""
BEGIN:VCALENDAR
PRODID:-//AT Content Types//AT Event//EN
VERSION:2.0
METHOD:PUBLISH
BEGIN:VEVENT
DTSTAMP:20080111T082529Z
CREATED:20080111T082344Z
UID:ATEvent-7a6801e8dda74e3af2216e5570ae2564
LAST-MODIFIED:20080111T082344Z
SUMMARY:eventtitle
DTSTART:20080111T082500Z
DTEND:20080111T092500Z
DESCRIPTION:eventdescription
LOCATION:eventlocation
CATEGORIES:another event category,an event category
CONTACT:event contact name\, 1223498765\, eventcontactemail@hurz.de
URL:http://www.eventurl.de
CLASS:PUBLIC
END:VEVENT
END:VCALENDAR
"""
MULTICALSTR="""
BEGIN:VCALENDAR
PRODID:-//AT Content Types//AT Event//EN
VERSION:2.0
METHOD:PUBLISH
BEGIN:VEVENT
DTSTAMP:20080111T082529Z
CREATED:20080111T082344Z
UID:ATEvent-7a6801e8dda74e3af2216e5570ae2564
LAST-MODIFIED:20080111T082344Z
SUMMARY:eventtitle
DTSTART:20080111T082500Z
DTEND:20080111T092500Z
DESCRIPTION:eventdescription
LOCATION:eventlocation
CATEGORIES:another event category,an event category
CONTACT:event contact name\, 1223498765\, eventcontactemail@hurz.de
URL:http://www.eventurl.de
CLASS:PUBLIC
END:VEVENT
BEGIN:VEVENT
DTSTAMP:20080111T082529Z
CREATED:20080111T082344Z
UID:ATEvent-7a6801e8dda74e3af2216e5570ae2564
LAST-MODIFIED:20080111T082344Z
SUMMARY:differenteventtitle
DTSTART:20080111T082500Z
DTEND:20080111T092500Z
DESCRIPTION:eventdescription
LOCATION:eventlocation
CATEGORIES:another event category,an event category
CONTACT:event contact name\, 1223498765\, eventcontactemail@hurz.de
URL:http://www.eventurl.de
CLASS:PUBLIC
END:VEVENT
END:VCALENDAR
"""

class TestEVTFactory(MailToPloneBaseTestCase):

    def afterSetUp(self):
        self.setRoles(('Manager',))

    def testUtilityLookup(self):
        self.failUnless(component.queryUtility(IEventFactory))

    def testFactoryCreatesATEvent(self):
        factory = component.queryUtility(IEventFactory)
        self.failUnless(factory.createEvent(ICALSTR, self.folder))
        self.failUnless("eventtitle" in self.folder.objectIds())

    def testFactoryPassesText(self):
        factory = component.queryUtility(IEventFactory)
        self.failUnless(factory.createEvent(ICALSTR, self.folder, text="thetext"))
        self.failUnless("<p>thetext</p>" == self.folder.eventtitle.getText())

class TestEVTFields(MailToPloneBaseTestCase):
    """ note: startDate and endDate are tested seperately in test_eventfactory_time.py """

    def afterSetUp(self):
        self.setRoles(('Manager',))
        factory = component.queryUtility(IEventFactory)
        factory.createEvent(ICALSTR, self.folder)

    def testEventTitle(self):
        self.failUnless(self.folder.eventtitle.title == "eventtitle")

    def testEventDescription(self):
        self.failUnless(self.folder.eventtitle.Description() == "eventdescription")

    def testEventLocation(self):
        self.failUnless(self.folder.eventtitle.location == "eventlocation")

    def testEventURL(self):
        self.failUnless(self.folder.eventtitle.eventUrl == "http://www.eventurl.de")

    def testEventType(self):
        self.failUnless(self.folder.eventtitle.eventType == (u'another event category', u'an event category'))

    def testEventContactName(self):
        self.failUnless(self.folder.eventtitle.contactName == u'event contact name')
        
    def testEventContactEmail(self):
        self.failUnless(self.folder.eventtitle.contactEmail == u'eventcontactemail@hurz.de')

    def testEventContactPhone(self):
        self.failUnless(self.folder.eventtitle.contactPhone == u'1223498765')

class TestEVTMult(MailToPloneBaseTestCase):

    def afterSetUp(self):
        self.setRoles(('Manager',))
        factory = component.queryUtility(IEventFactory)
        factory.createEvent(MULTICALSTR, self.folder)

    def testNumContents(self):
        self.failUnless(len(self.folder.objectIds()) == 2)

    def testEventsDiffer(self):
        e1 = self.folder.listFolderContents()[0]
        e2 = self.folder.listFolderContents()[1]
        self.failUnless(e1.title != e2.title)


class TestEVTInitialization(MailToPloneBaseTestCase):

    def afterSetUp(self):
        self.setRoles(('Manager',))
        self.factory = component.queryUtility(IEventFactory)

    def testEVTObjectInitializedEvent(self):
        self.sourceObject = None
        @adapter(IObjectInitializedEvent)
        def setSourceObject(new_event):
            self.sourceObject = new_event.object
        
        component.provideHandler(setSourceObject)
        self.factory.createEvent(ICALSTR, self.folder)
        self.failUnless(self.folder.listFolderContents()[0] == self.sourceObject)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestEVTFactory))
    suite.addTest(unittest.makeSuite(TestEVTFields))
    suite.addTest(unittest.makeSuite(TestEVTMult))
    suite.addTest(unittest.makeSuite(TestEVTInitialization))
    return suite

# vim: set ft=python ts=4 sw=4 expandtab :

