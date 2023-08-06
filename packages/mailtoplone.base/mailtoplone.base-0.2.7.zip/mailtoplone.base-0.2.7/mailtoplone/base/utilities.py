# -*- coding: utf-8 -*-
#
# File: utilities.py
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

import sys
import os
import logging

from DateTime import DateTime
from zope import component
from zope import interface
from zope import event

from zope.app.container.interfaces import INameChooser
from plone.i18n.normalizer.interfaces import IIDNormalizer

from Acquisition import aq_inner

from Acquisition import aq_base

from Products.CMFPlone.utils import getToolByName

import email
import icalendar
import dateutil

from Products.validation import validation

from Products.Archetypes.event import ObjectInitializedEvent

from mailtoplone.base import interfaces
from mailtoplone.base.myutils import dt2DT
from mailtoplone.base.events import MailDroppedEvent

class BaseDropBoxFactory(object):
    interface.implements(interfaces.IMailDropBoxFactory)

    def __call__(self, context, key):
        context = aq_inner(context)
        portal_catalog = getToolByName(context, "portal_catalog")
        brains = portal_catalog(
                id=key, 
                object_provides=interfaces.IMailDropBoxMarker.__identifier__, 
                effectiveRange=DateTime(),
                )
        for brain in brains:
            yield interfaces.IMailDropBox(brain.getObject())

class BodyFactory(object):
    interface.implements(interfaces.IBodyFactory)

    def __call__(self, mail):

        mailobj = email.message_from_string(mail)
        body_found = False
        for part in mailobj.walk():
            if part.get_content_type() == 'text/html' and not body_found:
                    body_found = True
                    body = part.get_payload(decode=1)
                    content_type = part.get_content_type()
                    charset = part.get_content_charset()

        for part in mailobj.walk():
            if part.get_content_type() == 'text/plain' and not body_found:
                    body_found = True
                    body = part.get_payload(decode=1)
                    content_type = part.get_content_type()
                    charset = part.get_content_charset()

        for part in mailobj.walk():
            if part.get_content_type() == 'text/rfc822' and not body_found:
                    body_found = True
                    body = part.get_payload(decode=1)
                    content_type = 'text/plain'
                    charset = part.get_content_charset()

        if not body_found:
                    body_found = True
                    body = ''
                    content_type = 'text/plain'
                    charset = None

        return body, content_type, charset


class ICalEventFactory(object):
    interface.implements(interfaces.IEventFactory)

    def createEvent(self, ical_str, context, **kw):

        normalizer = component.getUtility(IIDNormalizer)
        chooser = INameChooser(context)

        # get all VEVENT objects out of the ical_str
        events = []
        for eventobject in icalendar.Calendar.from_string(ical_str).walk(name='VEVENT'):
            events.append(eventobject)
            
        # extract VTIMEZONE Objects for startDate and endDate
        # 1. remove unsopported properties(X-) from ical_str
        li = ical_str.split('\n')
        clean_ical_str = "\n".join([item for item in li if not item.startswith('X-')])
        # 2. convert clean_ical_str to ical_file
        ical_file = os.tmpfile()
        ical_file.write(clean_ical_str)
        ical_file.seek(0)
        # 3. extract VTIMEZONES (there might be multiple VTIMEZONES in an calendar)
        tzones = dateutil.tz.tzical(ical_file)
        for eventobject in events:
            nkw = kw.copy()
            # generate the id
            source = 'SUMMARY'
            target = 'id'
            default = 'event'
            if not target in nkw.keys():
                if not source in eventobject.keys():
                    nkw[target] = chooser.chooseName(normalizer.normalize(default), aq_base(context))
                else:
                    nkw[target] = chooser.chooseName(normalizer.normalize(eventobject.decoded(source)), aq_base(context))
            else:
                nkw[target] = chooser.chooseName(normalizer.normalize(nkw[target]), aq_base(context))
 
            # generate the title
            source = 'SUMMARY'
            target = 'title'
            default = 'unnamed event'
            if not target in nkw.keys():
                if not source in eventobject.keys():
                    nkw[target] = default
                else:
                    nkw[target] = eventobject.decoded(source)
            
            # generate the description
            source = 'DESCRIPTION'
            target = 'description'
            default = ''
            if not target in nkw.keys():
                if not source in eventobject.keys():
                    nkw[target] = default
                else:
                    nkw[target] = eventobject.decoded(source)
            
            # generate the location
            source = 'LOCATION'
            target = 'location'
            default = ''
            if not target in nkw.keys():
                if not source in eventobject.keys():
                    nkw[target] = default
                else:
                    nkw[target] = eventobject.decoded(source)

            # generate the eventUrl
            source = 'URL'
            target = 'eventUrl'
            default = ''
            if not target in nkw.keys():
                if not source in eventobject.keys():
                    nkw[target] = default
                else:
                    nkw[target] = eventobject.decoded(source)

            # generate the eventType
            source = 'CATEGORIES'
            target = 'eventType'
            default = ''
            if not target in nkw.keys():
                if not source in eventobject.keys():
                    nkw[target] = default
                else:
                    nkw[target] = eventobject.get(source).split(",")

            # generate the startDate
            source = 'DTSTART'
            target = 'startDate'
            if not target in nkw.keys():
                if source in eventobject.keys():
                    if eventobject[source].params.has_key('TZID'):
                        tzone = tzones.get(eventobject[source].params['TZID'])
                        gmt_time = dt2DT(eventobject.decoded(source).replace(tzinfo=tzone))
                    else:
                        gmt_time = dt2DT(eventobject.decoded(source))
                    nkw[target] = gmt_time.toZone(gmt_time.localZone())

             # generate the endDate, it might be specified as DTEND, or as DTSTART + DURATION
            source = 'DTEND'
            source2 = 'DURATION'
            target = 'endDate'
            if not target in nkw.keys():
                if not source in eventobject.keys():
                    if 'DTSTART' in eventobject.keys() and source2 in eventobject.keys():
                        if eventobject['DTSTART'].params.has_key('TZID'):
                            tzone = tzones.get(eventobject['DTSTART'].params['TZID'])
                            gmt_time = dt2DT(eventobject.decoded('DTSTART').replace(tzinfo=tzone) + eventobject.decoded(source2))
                        else:
                            gmt_time = dt2DT(eventobject.decoded(DTSTART)+eventobject.decoded(source2))
                        nkw[target] = gmt_time.toZone(gmt_time.localZone())
                else:
                    if eventobject[source].params.has_key('TZID'):
                        tzone = tzones.get(eventobject[source].params['TZID'])
                        gmt_time = dt2DT(eventobject.decoded(source).replace(tzinfo=tzone))
                    else:
                        gmt_time = dt2DT(eventobject.decoded(source))
                    nkw[target] = gmt_time.toZone(gmt_time.localZone())

            # generate the contact fields
            source = 'CONTACT'
            clist = []
            if source in eventobject.keys():
                clist = eventobject.get(source).split(", ")
            
            # contact Email
            target = 'contactEmail'
            v = validation.validatorFor('isEmail')
            if not target in nkw.keys():
                    for elem in clist:
                        if v(str(elem)) == True:
                            nkw[target] = elem
                            clist.remove(elem)
                            break

            # contact phone
            target = 'contactPhone'
            v = validation.validatorFor('isInternationalPhoneNumber')
            if not target in nkw.keys():
                    for elem in clist:
                        if v(str(elem), ignore='[\\\(\)\-\s\+\/]') == True:
                            nkw[target] = elem
                            clist.remove(elem)
                            break
                    if (not target in nkw.keys()) and (len(clist) > 1):
                        nkw[target] = clist[1]
                        clist.remove(elem)
 
         # contact name
            target = 'contactName'
            if not target in nkw.keys():
                    for elem in clist:
                            nkw[target] = elem
                            break

         # attendees
         # There can be multiple "ATTENDEE" properties inside an VEVENT, the icalendar library returns a list of
         # vCalAddress objects if so, or otherwise a single vCalAddress object
         # we'll extract the CN (common name) if there is one inside and use it as an entry in the attendees linesfield
            source = 'ATTENDEE'
            target = 'attendees'
            if not target in nkw.keys():
                if source in eventobject.keys():
                    adrobjs = eventobject.get(source)
                    if type(adrobjs) == list:
                       nkw[target] = [item.params['CN'] for item in adrobjs if item.params.has_key('CN')]
                    elif adrobjs.params.has_key('CN'):
                       nkw[target] = [adrobjs.params['CN']]

            _ = context.invokeFactory("Event", **nkw)
            event.notify(ObjectInitializedEvent(getattr(context, nkw['id'], None)))
            event.notify(MailDroppedEvent(getattr(context, nkw['id'], None), context))

        return context.get(_)


# vim: set ft=python ts=4 sw=4 expandtab :
