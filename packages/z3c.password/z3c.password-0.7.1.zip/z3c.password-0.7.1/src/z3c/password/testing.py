##############################################################################
#
# Copyright (c) 2006 Lovely Systems and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Test Setup

$Id: testing.py 70891 2006-10-23 14:52:36Z rogerineichen $
"""
__docformat__ = "reStructuredText"

import zope.component
from zope.app.authentication import password
from zope.app.testing import placelesssetup


def setUp(test):
    placelesssetup.setUp(test)
    zope.component.provideUtility(
        password.PlainTextPasswordManager(), name='Plain Text')


def tearDown(test):
    placelesssetup.tearDown(test)
