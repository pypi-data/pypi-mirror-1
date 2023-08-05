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

from Acquisition import aq_inner

from Products.CMFPlone.utils import getToolByName

from mailtoplone.base import interfaces

import icalendar # the icalenadar library
from mailtoplone.base.myutils import dt2DT

# validtion for generating the contact fields
from Products.validation import validation

# we need to fire the ObjectInitializedEvent after creating each Event
from zope import event
from Products.Archetypes.event import ObjectInitializedEvent

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

class IdGenerator(object):
    interface.implements(interfaces.IIdGenerator)

    def generateId(self, context, id='item'):
        prefix = id
        ids = context.objectIds()
        nr = 0
        while id in ids:
            id = "".join([prefix,str(nr)])
            nr = nr + 1
        return id



class ICalEventFactory(object):
    interface.implements(interfaces.IEventFactory)

    def createEvent(self, ical_str, context, **kw):

        idgen = component.getUtility(interfaces.IIdGenerator)
        # get all VEVENT objects out of the ical_str
        events = []
        for eventobject in icalendar.Calendar.from_string(ical_str).walk(name='VEVENT'):
            events.append(eventobject)
            
        for eventobject in events:
            nkw = kw.copy()
            # generate the id
            source = 'SUMMARY'
            target = 'id'
            default = 'event'
            if not target in nkw.keys():
                if not source in eventobject.keys():
                    nkw[target] = idgen.generateId(context, default)
                else:
                    nkw[target] = idgen.generateId(context, eventobject.decoded(source))
            else:
                nkw[target] = idgen.generateId(context, nkw[target])
 
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
            default = ''
            if not target in nkw.keys():
                if not source in eventobject.keys():
                    nkw[target] = default
                else:
                    gmt_time = dt2DT(eventobject.decoded(source))
                    localised_time = gmt_time.toZone(gmt_time.localZone())
                    nkw[target] = localised_time

             # generate the endDate
            source = 'DTEND'
            target = 'endDate'
            default = ''
            if not target in nkw.keys():
                if not source in eventobject.keys():
                    nkw[target] = default
                else:
                    gmt_time = dt2DT(eventobject.decoded(source))
                    localised_time = gmt_time.toZone(gmt_time.localZone())
                    nkw[target] = localised_time

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


            _ = context.invokeFactory("Event", **nkw)
            event.notify(ObjectInitializedEvent(getattr(context, nkw['id'], None)))

        return context.get(_)


# vim: set ft=python ts=4 sw=4 expandtab :
