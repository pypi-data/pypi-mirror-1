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
$Id: interfaces.py 72087 2007-01-18 01:03:33Z rogerineichen $
"""

import zope.contentprovider.interfaces
from zope.publisher.interfaces.browser import IBrowserPage


class IPageletRenderer(zope.contentprovider.interfaces.IContentProvider):
    """Renders a pagelet by calling it's render method."""


class IPagelet(IBrowserPage):
    """The pagelet."""


class IPageletForm(IPagelet):
    """Form mixin for pagelet implementation."""


class IPageletAddForm(IPageletForm):
    """Add form mixin for pagelet implementation."""


class IPageletEditForm(IPageletForm):
    """Edit form mixin for pagelet implementation."""


class IPageletDisplayForm(IPageletForm):
    """FDisplay frm mixin for pagelet implementation."""
