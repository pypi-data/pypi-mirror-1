###############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
###############################################################################
"""
$Id: interfaces.py 72169 2007-01-22 08:29:30Z rogerineichen $
"""
__docformat__ = 'restructuredtext'


from zope.location.interfaces import ILocation
from zope.app.container.interfaces import IContainer



class IContainerLocationProxy(ILocation, IContainer):
    """Container proxy supporting a location."""