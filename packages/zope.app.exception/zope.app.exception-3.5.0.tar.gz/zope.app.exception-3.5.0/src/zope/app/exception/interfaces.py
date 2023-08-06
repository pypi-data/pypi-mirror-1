##############################################################################
# Copyright (c) 2003 Zope Corporation and Contributors.
# All Rights Reserved.
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
##############################################################################
"""General exceptions

$Id: interfaces.py 97488 2009-03-04 20:14:51Z nadako $
"""
__docformat__ = 'restructuredtext'

from zope.interface import Interface


class ISystemErrorView(Interface):
    """Error views that can classify their contexts as system errors
    """

    def isSystemError():
        """Return a boolean indicating whether the error is a system errror
        """
