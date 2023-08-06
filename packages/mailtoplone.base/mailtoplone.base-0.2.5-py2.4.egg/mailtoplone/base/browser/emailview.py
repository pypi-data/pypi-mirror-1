# -*- coding: utf-8 -*-
#
# File: emailview.py
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
from email.Header import decode_header
import urllib

from zope.interface import implements, Interface
from zope import component

from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Archetypes.utils import contentDispositionHeader

from plone.memoize.instance import memoize

from mailtoplone.base import baseMessageFactory as _
from mailtoplone.base.interfaces import IEmail
from mailtoplone.base.interfaces import IBodyFactory

class IEmailView(Interface):
    """
      EmailView interface
    """

    def test():
        """ test method"""



class EmailView(BrowserView):
    """
    EmailView for having a nice representation of the Email
    """
    implements(IEmailView)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    render = ViewPageTemplateFile('emailview.pt')

    def __call__(self):
        return self.render()

    @property
    def title(self):
        return self.context.title

    def decodeheader(self, header_text, default="ascii"):
        """Decode the specified header"""
        headers = decode_header(header_text)
        header_sections = [unicode(text, charset or default)
                       for text, charset in headers]
        return u"".join(header_sections)

    @memoize
    def headers(self):
        """
        returns a list of dicts like::

        [ { name="Subject", items=["muh", "mah"] }

        """
        headerlist = ['Subject','From','To','CC']
        adressheaders = headerlist[1:]
        m = email.message_from_string(self.context.data)
        for name in headerlist:
            if m.has_key(name):
                decoded = self.decodeheader(m[name])
                if name in adressheaders:
                    yield dict( name=name, contents=decoded.split(', ') )
                else:
                    yield dict( name=name, contents=[decoded] )


    def attachments(self):
        """return a generator which yields dicts like
            { "mimetype": "text/plain",
              "id":       "someidwhichisunique",
              "filename": "muha.txt" }
        """
        # we'll make an attachment for every part of the mail which has a
        # filename parameter
        m = email.message_from_string(self.context.data)
        parts = [item for item in m.walk() if item.get_filename() != None]
        for index, elem in enumerate(parts):
            charset = elem.get_content_charset() or "ISO-8859-1"
            mimetype= elem.get_content_type().decode(charset).encode("ascii", "ignore")
            fn= elem.get_filename().decode(charset).encode("ascii", "ignore")
            id = index
            url="%s/@@download?download=%s&mimetype=%s&filename=%s" % (
                self.context.absolute_url(),
                id,
                urllib.quote(mimetype),
                urllib.quote(fn) )
            yield dict(
                    mimetype=mimetype,
                    filename=fn,
                    id=id,
                    download_url=url
                    )

    @memoize
    def body(self):
        bodyfactory = component.getUtility(IBodyFactory)
        body, content_type, charset = bodyfactory(self.context.data)
        try:
            body = body.decode(charset).encode('utf-8')
        except (LookupError, TypeError):
            pass

        return dict(
                text=body,
                content_type=content_type,
                charset=charset,
                formatted=content_type == "text/html",
        )


    def test(self):
        """ 
        test method 
        """
        dummy = _(u'a dummy string')

        return {'dummy': dummy}


class AttachmentDownload(BrowserView):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        if self.request.get("download", None) is None:
            request.RESPONSE.redirect(self.context.absolute_url())

        m = email.message_from_string(self.context.data)
        parts = [item for item in m.walk() if item.get_filename() != None]
        if parts[int(self.request.get("download"))].is_multipart():
            data = str(parts[int(self.request.get("download"))])
        else:
            data = parts[int(self.request.get("download"))].get_payload(decode=1)
        REQUEST = self.request
        RESPONSE = REQUEST.RESPONSE
        filename = REQUEST.get("filename")
        mimetype = REQUEST.get("mimetype")
        if filename is not None:
            header_value = contentDispositionHeader(
                disposition='attachment',
                filename=filename)
            RESPONSE.setHeader("Content-disposition", header_value)
            RESPONSE.setHeader("Content-Type", mimetype)
        return data


# vim: set ft=python ts=4 sw=4 expandtab :
