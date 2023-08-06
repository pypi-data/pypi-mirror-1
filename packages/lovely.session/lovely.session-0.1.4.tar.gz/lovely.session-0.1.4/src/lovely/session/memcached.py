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
$Id: memcached.py 89092 2008-07-31 14:34:22Z srichter $
"""
__docformat__ = 'restructuredtext'
import md5
import cPickle
import memcache
import time
from threading import local

import persistent
import transaction
from transaction.interfaces import IDataManager

from zope import interface
from zope import component

from zope.schema.fieldproperty import FieldProperty

from zope.app.container.contained import Contained
from zope.session.interfaces import (
    ISessionDataContainer,
    ISessionData,
    ISessionPkgData,
    )
from zope.session.session import PersistentSessionDataContainer

from lovely.memcached.interfaces import IMemcachedClient
from lovely.session.interfaces import IMemCachedSessionDataContainer


class MemCachedSessionDataContainer(persistent.Persistent, Contained):
    interface.implements(ISessionDataContainer, IMemCachedSessionDataContainer)

    cacheName = FieldProperty(IMemCachedSessionDataContainer['cacheName'])

    def __init__(self):
        self.resolution = 5*60
        self.timeout = 1 * 60 * 60

    def get(self, key, default=None):
        return self[key]

    def __contains__(self, key):
        return key in self.dataManagers

    def __getitem__(self, key):
        # getitem never fails to make sure the session uses our own PkgData
        # implementation.
        if key in self.dataManagers:
            dm = self.dataManagers[key]
        else:
            dm = DataManager(self, key)
            txn = transaction.manager.get()
            txn.join(dm)
            self.dataManagers[key] = dm
            item = self.client.query(self._buildKey(key))
            if item is None:
                item = MemCacheSessionData()
            dm.data = item
        return dm.data

    def __setitem__(self, key, value):
        pass

    def items(self):
        return self.dataManagers.items()

    def _commitManager(self, key):
        if key in self.dataManagers:
            dm = self.dataManagers[key]
            if not dm.changed:
                del self.dataManagers[key]
                return
            if self.client.set(dm.data,
                               self._buildKey(key),
                               self.timeout):
                del self.dataManagers[key]

    def _abortManager(self, key):
        #TODO: ???
        if key in self.dataManagers:
            del self.dataManagers[key]

    def _buildKey(self, key):
        m = md5.new(key)
        return 'lovely.session.memcached:%s/%s'%(
                    self.__name__.encode('utf-8'),
                    m.hexdigest())

    @property
    def dataManagers(self):
        res = getattr(self.storage, 'dataManagers', None)
        if res is None:
            res = {}
            self.storage.dataManagers = res
        return res

    @property
    def client(self):
        return component.getUtility(IMemcachedClient, self.cacheName)

    @property
    def storage(self):
        # we use a thread local storage to have a memcache client for every
        # thread.
        if not hasattr(self, '_v_storage'):
            self._v_storage = local()
        return self._v_storage


class MemCacheData(dict):
    """See zope.session.interfaces.ISessionData
    """
    interface.implements(ISessionPkgData)


class MemCacheSessionData(dict):
    """See zope.session.interfaces.ISessionData"""
    interface.implements(ISessionData)
    lastAccessTime = 0

    def __init__(self):
        self.lastAccessTime = int(time.time())

    def __getitem__(self, key):
        try:
            return super(MemCacheSessionData, self).__getitem__(key)
        except KeyError:
            data = MemCachePkgData()
            self[key] = data
            return data


class MemCachePkgData(dict):
    """"""
    interface.implements(ISessionPkgData)


class DataManager(object):
    """A data manager for the transaction management of the session data"""
    interface.implements(IDataManager)

    def __init__(self, sessionData, key):
        self.sessionData = sessionData
        self._data = None
        self.key = key

    @apply
    def data():
        def get(self):
            return self._data
        def set(self, value):
            self._data = value
            self._oldData = cPickle.dumps(value)
        return property(get, set)

    @property
    def changed(self):
        return cPickle.dumps(self.data)!=self._oldData

    def abort(self, trans):
        self.sessionData._abortManager(self.key)

    def tpc_begin(self, trans):
        pass

    def commit(self, trans):
        pass

    def tpc_vote(self, trans):
        pass

    def tpc_finish(self, trans):
        self.sessionData._commitManager(self.key)

    def tpc_abort(self, trans):
        self.sessionData._abortManager(self.key)

    def sortKey(self):
        return str(id(self))

