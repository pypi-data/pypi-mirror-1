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
$Id: __init__.py 96515 2009-02-14 07:05:42Z icemac $
"""

from zope.publisher.interfaces.browser import IBrowserRequest

import warnings

warnings.warn(
    'Package z3c.layer is retired, please use z3c.layer.minimal package.',
    DeprecationWarning,
    stacklevel=2)


class IMinimalBrowserLayer(IBrowserRequest):
    """Like IDefaultBrowserLayer but only with the most important views."""
