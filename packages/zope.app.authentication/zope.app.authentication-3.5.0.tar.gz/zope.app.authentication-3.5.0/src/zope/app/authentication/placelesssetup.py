##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Pluggable Authentication Service Placeless Setup

$Id: placelesssetup.py 97567 2009-03-06 12:40:59Z nadako $
"""
__docformat__ = "reStructuredText"

# BBB: the password managers were moved to zope.password package
from zope.password.testing import setUpPasswordManagers

class PlacelessSetup(object):

    def setUp(self):
        setUpPasswordManagers()
