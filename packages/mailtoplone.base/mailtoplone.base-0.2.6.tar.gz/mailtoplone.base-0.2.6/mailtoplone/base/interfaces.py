# -*- coding: utf-8 -*-
#
# File: interfaces.py
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


from zope import component
from zope import interface
from zope import schema


from zope.app.container.constraints import contains
from zope.app.container.constraints import containers


from mailtoplone.base import baseMessageFactory as _

# Interfaces go here ...
# -*- extra stuff goes here -*-

class IInBox(interface.Interface):
    """A folderish type containing Emails"""

class IEmail(interface.Interface):
    """A file like content containing an email"""

# SELETZ
class IMailDropBoxMarker(interface.Interface):
    """ marker interface for mail drop boxes """

class IMailDropBox(interface.Interface):
    """ a mail drop box """
    def drop(mail):
        """ drop a mail into this mail box. The mail is
            a string with the complete email content """

class IMailDropBoxFactory(interface.Interface):
    """ a factory for mail drop boxes """

    def __call__(context, key):
        """ look up drop boxes based on context and key, and return a list of
        objects providing IMailDropBox """
# /SELETZ

class IBlogMailDropBoxMarker(IMailDropBoxMarker):
    """ marker interface for blog mail drop boxes """

class IEventMailDropBoxMarker(IMailDropBoxMarker):
    """ marker interface for event mail drop boxes """

class IEventFactory(interface.Interface):
    """ creates a AT Event out of something. Keyword args
        are passed to invokeFactory() """

    def createEvent(source, context, **kwargs ):
        """ create a event in some context """

__doc__ = """
    >>> event_dict_with_atevent_keys = {} # leeres dict
    >>> event_dict_with_atevent_keys.update(kwargs) # dict mit default von user füllen
    >>> utils.icalparse(icalobj, event_dict_with_atevent_keys) # dict weiter füllen mit ical stuff
    >>> _ = self.folder.invokeFactory("ATEvent", "evt", **event_dict_with_atevent_keys ) # create atevent
    >>> obj = self.folder.get(_)

    ...

    >>> kw = dict( title="zonk", hurz="muha", body=file("/tmp/xxx").read() )
    >>> obj.update( **kw )

    ... 

"""

class IICalEventFactory(IEventFactory):
    """ iCal Object to AT Event factory """

    def createEvent(icalevt, context, **kwargs ):
        """ creates an AT Event out of an iCal object """

class IBodyFactory(interface.Interface):
    """ extract a body and a content_type from a mail string"""

    def __call__(mail):
        """ go through mail and return a body and a content_type """

class IMailDroppedEvent(component.interfaces.IObjectEvent):
    object = interface.Attribute("The mail object of the event.")
    context = interface.Attribute("The context of the event.")

# vim: set ft=python ts=4 sw=4 expandtab :
