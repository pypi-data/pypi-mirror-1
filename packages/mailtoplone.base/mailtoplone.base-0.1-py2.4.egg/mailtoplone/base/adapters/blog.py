# -*- coding: utf-8 -*-
#
# File: blog.py
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


from zope import interface, component

from mailtoplone.base.interfaces import IMailDropBox, IIdGenerator
import email

class BlogMailDropBox(object):
    """ adapts IBlogMailDropBoxmarker to a IMailDropBox """

    interface.implements(IMailDropBox)

    def __init__(self, context):
        self.context = context

    def drop(self, mail):
        """ drop a mail into this mail box. The mail is
        a string with the complete email content """

        mailobj = email.message_from_string(mail)
        body_found = False
        for part in mailobj.walk():
            if part.get_content_type() == 'text/html' and not body_found:
                    body_found = True
                    body = part.get_payload(decode=1)
                    format = part.get_content_type()
                    content_type = part.get_content_type()

        for part in mailobj.walk():
            if part.get_content_type() == 'text/plain' and not body_found:
                    body_found = True
                    body = part.get_payload(decode=1)
                    format = part.get_content_type()
                    content_type = part.get_content_type()

        for part in mailobj.walk():
            if part.get_content_type() == 'text/rfc822' and not body_found:
                    body_found = True
                    body = part.get_payload(decode=1)
                    format = 'text/plain'
                    content_type = 'text/plain'

        if not body_found:
                    body_found = True
                    body = "Fooooo"
                    format = 'text/plain'
                    content_type = 'text/plain'

        #start description extraction
        # todo: get a description from the email

        text = "XXX"
        type = 'News Item'
        description='todo'
        # generate id
        idgen = component.getUtility(IIdGenerator)
        id = idgen.generateId(self.context, 'news')

        self.context.invokeFactory(type ,id=id , title=id, format=format, \
                                   content_type=content_type, description=text, text=body)

        getattr(self.context, id, None).processForm()

        
# vim: set ft=python ts=4 sw=4 expandtab :
