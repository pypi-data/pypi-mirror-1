##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" CMFDefault.interfaces package.

$Id: __init__.py 73215 2007-03-16 08:55:04Z yuppie $
"""

from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from _content import *
from _tools import *


class ICMFDefaultSkin(IDefaultBrowserLayer):

    """CMF default skin.
    """
