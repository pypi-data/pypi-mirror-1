# -*- coding: utf-8 -*-
#
# File: xmlrpcview.py
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

from zope.interface import implements, Interface

from Products.Five import BrowserView

from mailtoplone.base import baseMessageFactory as _
from mailtoplone.base.interfaces import IMailDropBox

class IXMLRPCView(Interface):
    """
      XMLRPCView interface
    """
    
    def test():
        """ test method"""
    

            
class XMLRPCView(BrowserView):
    """
    xmlrpcview for using drop via xmlrpc
    """
    implements(IXMLRPCView)
        
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def drop(self, mail):
        """calls the adapter to drop a mail into an InBox"""
        IMailDropBox(self.context).drop(mail)
    
    
    def test(self):
        """ 
        test method 
        """
        dummy = _(u'a dummy string')
        
        return {'dummy': dummy}

# vim: set ft=python ts=4 sw=4 expandtab :
