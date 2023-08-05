##############################################################################
#
# Copyright (c) 2005 Zope Foundation and Contributors.
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
"""
$Id: provider.py 72087 2007-01-18 01:03:33Z rogerineichen $
"""

import zope.interface
import zope.component
from zope.publisher.interfaces import browser

from z3c.pagelet import interfaces


class PageletRenderer(object):
    """Render the adapted pagelet."""

    zope.interface.implements(interfaces.IPageletRenderer)

    zope.component.adapts(zope.interface.Interface, browser.IBrowserRequest,
        interfaces.IPagelet)

    def __init__(self, context, request, pagelet):
        self.__updated = False
        self.__parent__ = pagelet
        self.context = context
        self.request = request

    def update(self):
        pass

    def render(self):
        return self.__parent__.render()
