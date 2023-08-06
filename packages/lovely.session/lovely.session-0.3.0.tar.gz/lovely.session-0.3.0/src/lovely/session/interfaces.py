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
$Id: interfaces.py 106425 2009-12-11 07:20:25Z fafhrd $
"""
__docformat__ = 'restructuredtext'

from zope import interface
from zope import schema


class IMemCachedSessionDataContainer(interface.Interface):
    """A session container using memcache"""

    cacheName = schema.TextLine(title=u'Cachename',
                                required=False,
                                default=u'')
