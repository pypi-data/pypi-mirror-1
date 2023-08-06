##############################################################################
#
# Copyright (c) 2007 Lovely Systems and Contributors.
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
$Id: interfaces.py 82223 2007-12-10 12:59:59Z schwendinger $
"""
__docformat__ = 'restructuredtext'

from zope import interface
from zope import schema


class IMemCachedSessionDataContainer(interface.Interface):
    """A session container using memcache"""

    cacheName = schema.TextLine(title=u'Cachename',
                                required=False,
                                default=u'')

