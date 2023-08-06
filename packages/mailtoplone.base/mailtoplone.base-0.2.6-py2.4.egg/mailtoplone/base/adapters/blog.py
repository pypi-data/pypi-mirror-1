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

import email
import logging

from zope import interface
from zope import component
from zope.event import notify

from zope.app.container.interfaces import INameChooser
from plone.i18n.normalizer.interfaces import IIDNormalizer

from Acquisition import aq_base

from mailtoplone.base.interfaces import IMailDropBox
from mailtoplone.base.interfaces import IBodyFactory
from mailtoplone.base.events import MailDroppedEvent

info = logging.getLogger().info

class BlogMailDropBox(object):
    """ adapts IBlogMailDropBoxmarker to a IMailDropBox """

    interface.implements(IMailDropBox)

    def __init__(self, context):
        self.context = context

    def drop(self, mail):
        """ drop a mail into this mail box. The mail is
        a string with the complete email content """
        
        # get the body and matching content_type, charset
        bodyfactory = component.queryUtility(IBodyFactory)
        body, content_type, charset = bodyfactory(mail)
        format = content_type

        mailobj = email.message_from_string(mail)

        # Subject and description
        for key in "Subject subject Betreff x-blog-title".split():
            subject = mailobj.get(key)
            if subject is not None:
                break
        description = mailobj.get("x-blog-description", "")

        info( "BlogMailDropBox: new mail with subject '%s'" % subject )

        # XXX: the namechooer does a getattr('check_id'), which results in a python
        #      script (!!) which is aquired. That script makes the name chooser not choose
        #      correctly, thus we strip acquisition. Bah.
        normalizer = component.getUtility(IIDNormalizer)
        chooser = INameChooser(self.context)
        id = chooser.chooseName(normalizer.normalize(subject), aq_base(self.context))

        self.context.invokeFactory(
                'News Item',
                id=id,
                title=subject,
                format=format,
                content_type=content_type,
                description=description,
                text=body
                )

        news = getattr(self.context, id)
        news.processForm()
        notify(MailDroppedEvent(news, self.context))

# vim: set ft=python ts=4 sw=4 expandtab :
