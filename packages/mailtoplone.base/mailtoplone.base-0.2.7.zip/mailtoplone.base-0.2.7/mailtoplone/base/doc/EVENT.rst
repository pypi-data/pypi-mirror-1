EVENT
=====

Abstract
--------

This is a test for the mailtoplone.base EventMailDropBox


Setup test environment::

    >>> self.setRoles(('Manager',))

Create a folder and mark with the IEventMailDropBoxMarker::

    >>> from zope.interface import alsoProvides
    >>> from mailtoplone.base.interfaces import IEventMailDropBoxMarker
    >>> self.portal.invokeFactory('Folder', 'efolder')
    'efolder'
    >>> alsoProvides(self.portal.efolder, IEventMailDropBoxMarker)
    >>> IEventMailDropBoxMarker.providedBy(self.portal.efolder)
    True

Now that the folder is marked we can use our adapter on it::

    >>> from mailtoplone.base.interfaces import IMailDropBox
    
Let's use an email containing text/calendar attachments::

    >>> import os
    >>> directory = os.path.dirname(__file__)
    >>> f = open(os.path.join(directory, 'calendars.eml'))

The mail contains two attachments, the first attachment contains a calendar
containing two VEVENTs, the second contains a calendar consisting of a
single VEVENT. So after dropping the email to our EventMailDropBox, there
should be 3 events inside::

    >>> IMailDropBox(self.portal.efolder).drop(f.read())
    >>> len(self.portal.efolder.objectIds())
    3
    >>> self.portal.efolder.listFolderContents()[0].meta_type
    'ATEvent'
    >>> self.portal.efolder.listFolderContents()[1].meta_type
    'ATEvent'
    >>> self.portal.efolder.listFolderContents()[2].meta_type
    'ATEvent'

::

    vim: set ft=rst tw=75 nocin nosi ai sw=4 ts=4 expandtab:

