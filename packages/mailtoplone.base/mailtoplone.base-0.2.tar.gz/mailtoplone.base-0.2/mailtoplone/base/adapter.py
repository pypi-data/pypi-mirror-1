# -*- coding: utf-8 -*-
#
# File: adapter.py
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
from zope.app.container.interfaces import INameChooser
from plone.i18n.normalizer.interfaces import IIDNormalizer
     
from Acquisition import aq_base

from mailtoplone.base.interfaces import IMailDropBox

class MailDropBox(object):
    """ adapts a IMailDropBoxMarker to a IMailDropBox """

    interface.implements(IMailDropBox)

    def __init__(self, context):
        self.context = context

    def drop(self, mail):
        """ drop a mail into this mail box. The mail is
        a string with the complete email content """
        
        # code unicode to utf-8
        if isinstance(mail,unicode):
            mail = mail.encode( 'utf-8' )
        type = 'Email'
        format = 'text/plain'
        content_type='text/plain'
        # generate id
        normalizer = component.getUtility(IIDNormalizer)
        chooser = INameChooser(self.context)
        id = chooser.chooseName(normalizer.normalize('email'), aq_base(self.context))
        
        self.context.invokeFactory(type ,id=id , title=id, format=format, \
                                   content_type=content_type, file=mail)
        getattr(self.context, id, None).setContentType(content_type)
        getattr(self.context, id, None).processForm()
        
# vim: set ft=python ts=4 sw=4 expandtab :
