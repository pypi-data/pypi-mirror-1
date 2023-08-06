# -*- coding: utf-8 -*-
#
# File: event.py
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

__author__    = """Hans-Peter Locher<hans-peter.locher@inquant.de>"""
__docformat__ = 'plaintext'
__revision__  = "$Revision: 36831 $"
__version__   = '$Revision: 1.7 $'[11:-2]

from zope import interface
from zope import component

import email

from mailtoplone.base.interfaces import IMailDropBox
from mailtoplone.base.interfaces import IEventFactory
from mailtoplone.base.interfaces import IBodyFactory

class EventMailDropBox(object):
    """ adapts IEventMailDropBoxmarker to a IMailDropBox """

    interface.implements(IMailDropBox)

    def __init__(self, context):
        self.context = context

    def drop(self, mail):
        """ drop a mail into this mail box. The mail is
        a string with the complete email content """

        factory = component.queryUtility(IEventFactory)
        # get the body and matching content_type, charset
        bodyfactory = component.queryUtility(IBodyFactory)
        body, content_type, charset = bodyfactory(mail)
        format = content_type

        mailobj = email.message_from_string(mail)
        
        # passing the calendars to the EventFactory
        for part in mailobj.walk():
            if part.get_content_type() == 'text/calendar':
                ics = part.get_payload(decode=1)
                factory.createEvent(
                        ics,
                        self.context,
                        content_type=content_type,
                        format=format,
                        text=body
                        )

# vim: set ft=python ts=4 sw=4 expandtab :
