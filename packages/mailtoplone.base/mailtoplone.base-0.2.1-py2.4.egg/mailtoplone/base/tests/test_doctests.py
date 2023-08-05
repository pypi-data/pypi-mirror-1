# -*- coding: utf-8 -*-
#
# File: test_doctests.py
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

__author__    = """Hans-Peter Locher <hans-peter.locher@inquant.de>"""
__docformat__ = 'plaintext'


import unittest
import doctest

from Testing import ZopeTestCase as ztc

from mailtoplone.base.tests import base


doctests = [
        'README.rst',
        'doc/BLOG.rst',
        'doc/EVENT.rst',
        ]

def test_suite():
    return unittest.TestSuite([

        ztc.ZopeDocFileSuite(
            dtfile, package='mailtoplone.base',
            test_class=base.MailToPloneBaseFunctionalTestCase,

            optionflags=(
                doctest.NORMALIZE_WHITESPACE |
                doctest.ELLIPSIS |
                doctest.REPORT_ONLY_FIRST_FAILURE
                )
            )

            for dtfile in doctests
            ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

# vim: set ft=python ts=4 sw=4 expandtab :
