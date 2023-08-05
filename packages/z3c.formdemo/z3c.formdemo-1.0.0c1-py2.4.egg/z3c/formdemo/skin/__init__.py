##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
$Id: __init__.py 217 2007-04-15 20:25:48Z rineichen $
"""
__docformat__ = "reStructuredText"

from zope.viewlet.interfaces import IViewletManager
from zope.viewlet.viewlet import CSSViewlet
from zope.viewlet.viewlet import JavaScriptViewlet
from z3c.pagelet import browser
from z3c.formui import interfaces
from z3c.formdemo import layer


class IDivDemoBrowserSkin(interfaces.IDivFormLayer, layer.IDemoBrowserLayer):
    """The ``Z3CFormDemo`` browser skin."""


class ITableDemoBrowserSkin(interfaces.ITableFormLayer, 
    layer.IDemoBrowserLayer):
    """The ``Z3CTableFormDemo`` browser skin."""


class ICSS(interfaces.ICSS):
    """CSS viewlet manager."""


class IJavaScript(IViewletManager):
    """JavaScript viewlet manager."""


DemoCSSViewlet = CSSViewlet('demo.css')
DemoJavaScriptViewlet = JavaScriptViewlet('demo.js')

