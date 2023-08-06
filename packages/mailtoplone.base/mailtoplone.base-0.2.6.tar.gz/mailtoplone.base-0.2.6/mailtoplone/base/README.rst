mailtoplone.base
================

Setup TestEnvironment
---------------------

Setting up a inbox containing email1, email2::

    >>> self.setRoles(('Manager',))
    >>> self.portal.invokeFactory('InBox', 'inbox')
    'inbox'
    >>> self.portal.inbox.invokeFactory('Email', 'email1')
    'email1'
    >>> self.portal.inbox.invokeFactory('Email', 'email3')
    'email3'

Adapter
-------

Let's test the drop function useable with the MailDropBox Adapter,
The dropped mails get their id's using the NameChooser::

    >>> from mailtoplone.base.interfaces import IMailDropBox
    >>> IMailDropBox(self.portal.inbox).drop("some data")
    >>> IMailDropBox(self.portal.inbox).drop("some data")
    >>> IMailDropBox(self.portal.inbox).drop("some data")
    >>> self.portal.inbox.objectIds()
    ['email1', 'email3', 'email', 'email-1', 'email-2']

Let's test some values of a created email::

    >>> self.portal.inbox.email.title
    'email'
    >>> self.portal.inbox.email.data
    'some data'
    >>> self.portal.inbox.email.meta_type
    'Email'


Browserview xmlrpcview
----------------------

Let's test if the xmlrpcview has a drop method which creates an Email in
the inbox::

    >>> theview = self.portal.inbox.restrictedTraverse('xmlrpcview')
    >>> theview.drop("dropped via view")
    >>> self.portal.inbox.objectIds()
    ['email1', 'email3', 'email', 'email-1', 'email-2', 'email-3']
    >>> self.portal.inbox.listFolderContents()[5].data
    'dropped via view'

Email title
-----------

We generate the tile for email objects out of the subject, otherwise we'll
take the id.

First, let's create various minimalistic emails::

    >>> withsubject = 'subject: withsubject'
    >>> withSubject = 'Subject: withSubject'
    >>> withbetreff = 'betreff: withbetreff'
    >>> withBetreff = 'Betreff: withBetreff'

Let's drop this emails to our inbox::

    >>> theview.drop(withsubject)
    >>> self.portal.inbox.listFolderContents()[6].Title()
    'withsubject'

    >>> theview.drop(withSubject)
    >>> self.portal.inbox.listFolderContents()[7].Title()
    'withSubject'

    >>> theview.drop(withbetreff)
    >>> self.portal.inbox.listFolderContents()[8].Title()
    'withbetreff'

    >>> theview.drop(withBetreff)
    >>> self.portal.inbox.listFolderContents()[9].Title()
    'withBetreff'

If we have multiple subject / betreff / ... in our mail, let's take the
first Subject::

    >>> theview.drop('Subject: SUB\nBetreff: BET')
    >>> self.portal.inbox.listFolderContents()[10].Title()
    'SUB'

We decode the subject header for presentation, let's drop an encoded subject::

    >>> theview.drop('Subject: =?ISO-8859-15?Q?=FCld=F6m?=')
    >>> self.portal.inbox.listFolderContents()[11].Title() == 'üldöm'
    True

::

    vim: set ft=rst tw=75 nocin nosi ai sw=4 ts=4 expandtab:

