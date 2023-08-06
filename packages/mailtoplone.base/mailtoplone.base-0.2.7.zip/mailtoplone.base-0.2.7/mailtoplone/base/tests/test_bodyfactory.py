# -*- coding: utf-8 -*-
#
# File: test_bodyfactory.py
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

from mailtoplone.base.tests.base import MailToPloneBaseTestCase
from mailtoplone.base.interfaces import IBodyFactory

MULTIONEPLAIN="""MIME-Version: 1.0
Content-Type: multipart/mixed;
	boundary="next"

--next
Content-Type: text/plain;

plain content
--next
Content-Type: text/calendar;

other content
--next--
"""

MULTITWOPLAIN="""MIME-Version: 1.0
Content-Type: multipart/mixed;
	boundary="next"

--next
Content-Type: text/plain; charset=xy-charset;

plain content1
--next
Content-Type: text/plain;

plain content2
--next--
"""

MULTIONEHTML="""MIME-Version: 1.0
Content-Type: multipart/mixed;
	boundary="next"

--next
Content-Type: text/plain;

plain content
--next
Content-Type: text/html; charset=iso-8859-1;

html content
--next--
"""

MULTITWOHTML="""MIME-Version: 1.0
Content-Type: multipart/mixed;
	boundary="next"

--next
Content-Type: text/html;

html content1
--next
Content-Type: text/html;

html content2
--next--
"""

MULTIONERFC822="""MIME-Version: 1.0
Content-Type: multipart/mixed;
	boundary="next"

--next
Content-Type: text/rfc822;

rfc822 content
--next
Content-Type: text/calendar;

other content
--next--
"""

MULTITWORFC822="""MIME-Version: 1.0
Content-Type: multipart/mixed;
	boundary="next"

--next
Content-Type: text/rfc822;

rfc822 content1
--next
Content-Type: text/rfc822;

rfc822 content2
--next--
"""

MULTIOTHER="""MIME-Version: 1.0
Content-Type: multipart/mixed;
	boundary="next"

--next
Content-Type: text/calendar;

other content1
--next
Content-Type: video/mpeg;

other content2
--next--
"""

class TestBodyFactory(MailToPloneBaseTestCase):

    def afterSetUp(self):
        self.setRoles(('Manager',))
        self.factory = component.queryUtility(IBodyFactory)

    def test_multioneplain(self):
        body, content_type, charset = self.factory(MULTIONEPLAIN)
        self.assertEquals(body,'plain content')
        self.assertEquals(content_type,'text/plain')
        self.assertEquals(charset,None)

    def test_multitwoplain(self):
        body, content_type, charset = self.factory(MULTITWOPLAIN)
        self.assertEquals(body,'plain content1')
        self.assertEquals(content_type,'text/plain')
        self.assertEquals(charset,'xy-charset')

    def test_multionehtml(self):
        body, content_type, charset= self.factory(MULTIONEHTML)
        self.assertEquals(body,'html content')
        self.assertEquals(content_type,'text/html')
        self.assertEquals(charset,'iso-8859-1')

    def test_multitwohtml(self):
        body, content_type, charset = self.factory(MULTITWOHTML)
        self.assertEquals(body,'html content1')
        self.assertEquals(content_type,'text/html')
        self.assertEquals(charset,None)

    def test_multionerfc822(self):
        body, content_type, charset = self.factory(MULTIONERFC822)
        self.assertEquals(body,'rfc822 content')
        self.assertEquals(content_type,'text/plain')
        self.assertEquals(charset,None)

    def test_multitworfc822(self):
        body, content_type, charset = self.factory(MULTITWORFC822)
        self.assertEquals(body,'rfc822 content1')
        self.assertEquals(content_type,'text/plain')
        self.assertEquals(charset,None)

    def test_multiother(self):
        body, content_type, charset = self.factory(MULTIOTHER)
        self.assertEquals(body,'')
        self.assertEquals(content_type,'text/plain')
        self.assertEquals(charset,None)

    def test_noemail(self):
        body, content_type, charset = self.factory("")
        self.assertEquals(body,'')
        self.assertEquals(content_type,'text/plain')
        self.assertEquals(charset,None)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestBodyFactory))
    return suite

# vim: set ft=python ts=4 sw=4 expandtab :

