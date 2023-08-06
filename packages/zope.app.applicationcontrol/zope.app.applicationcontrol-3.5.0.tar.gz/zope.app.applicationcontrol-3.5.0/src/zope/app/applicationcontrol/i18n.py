##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Customization of zope.i18n for the Zope application server

$Id: i18n.py 100320 2009-05-23 22:08:03Z shane $
"""
__docformat__ = 'restructuredtext'

# import this as _ to create i18n messages in the zope domain
from zope.i18nmessageid import MessageFactory
ZopeMessageFactory = MessageFactory('zope')
