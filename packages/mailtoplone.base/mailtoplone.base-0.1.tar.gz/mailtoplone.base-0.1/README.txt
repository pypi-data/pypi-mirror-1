mailtoplone.base
================

Overview
--------

basic package for mailtoplone

Authors
-------

Stefan Eletzhofer --
    "stefan.eletzhofer@inquant.de"

Hans-Peter Locher --
    "hans-peter.locher@inquant.de"

Copyright (c) 2007-2008 InQuant GmbH -- "http://www.inquant.de"

Dependencies
------------

Additional egg dependecies
**************************

icalendar
dateutil

Contents
--------

Content Types
*************

InBox:

    Provides an XMLRPCView to access it's drop method.
    Dropping a mailstring ( a plaintext string containing the whole email including envelope),
    a plone content type Email will be generated, the data field will contain the mailstring.

Email:
    
    File like content type conatining the mailstring inside the data field

Adapters
********

MailDropBox:
                
    Basic adapter, providing a drop method generating an Email out of the dropped mailstring

BlogMailDropBox:

    Advanced adapter, creating a news item out of the dropped mailstring.

EventMailDropBox:

    Advanced adapter, creating an event out of text/calendar attachments inside the dropped mailstring

Utilities
*********

BaseDropBoxFactory:

    Used to find objects providing IMailDropBoxMarker with id=key. Used by
    the deliver action in mailtoplone.contentrules.

IdGenerator:

    Used to generate a simple id unique for the given context. Used when
    generating content (Emails, News, Events)

ICalEventFactory:

    Taking an icalendar string, this utility creates an ATEvent out of each
    VEVENT. The implementation supports keywordarguments, passing them to
    invokeFactory. 
    This implementation correctly imports events exported from plone, as a
    first approach.
    It is used by the EventMailDropBox.

MarkerInterfaces
****************

You can use these markerinterfaces (@@manage_interfaces) to mark a folder
for mailtoplone (remember to reindex the marked object). Afterwards the
folder can be found and delivered mails to.

IMailDropBoxMarker(Interface):
    """ marker interface for mail drop boxes """

IBlogMailDropBoxMarker(IMailDropBoxMarker):
    """ marker interface for blog mail drop boxes """

IEventMailDropBoxMarker(IMailDropBoxMarker):
    """ marker interface for event mail drop boxes """

Scripts
*******

dropemail:

    File system python script, to drop a mail to an inbox(url), specify the mail as file or use stdin

vim: set ft=rst tw=75 nocin nosi ai sw=4 ts=4 expandtab:
